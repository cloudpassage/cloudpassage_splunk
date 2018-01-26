import os
import sys
import lib
import json
import splunklib.client as client
import lib.validate as validate
import lib.date_util as dateUtil

from splunklib.modularinput import *

class MyScript(Script):
    # Define some global variables
    MASK           = "<nothing to see here>"
    APP            = __file__.split(os.sep)[-3]
    USERNAME       = None
    CLEAR_PASSWORD = None

    def get_scheme(self):
        scheme = Scheme("CloudPassage Splunk Connector")
        scheme.description = ("Demonstrates how to encrypt/decrypt credentials in modular inputs.")
        scheme.use_external_validation = True
        scheme.streaming_mode_xml = True
        scheme.use_single_instance = False

        api_key_arg = Argument(
            name="api_key",
            title="API Key",
            data_type=Argument.data_type_string,
            required_on_create=True,
            required_on_edit=True
        )
        scheme.add_argument(api_key_arg)

        secret_key_arg = Argument(
            name="secret_key",
            title="API Secret Key",
            data_type=Argument.data_type_string,
            required_on_create=True,
            required_on_edit=True
        )
        scheme.add_argument(secret_key_arg)

        hostname_arg = Argument(
            name="api_host",
            title="API Hostname",
            data_type=Argument.data_type_string,
            required_on_create=True,
            required_on_edit=True
        )
        scheme.add_argument(hostname_arg)

        port_arg = Argument(
            name="api_port",
            title="API Port",
            data_type=Argument.data_type_string,
            required_on_create=True,
            required_on_edit=True
        )
        scheme.add_argument(port_arg)

        start_date_arg = Argument(
            name="start_date",
            title="Start Date. (If checkpoint exists, it will take precedence)",
            data_type=Argument.data_type_string,
            required_on_create=False,
            required_on_edit=False
        )
        scheme.add_argument(start_date_arg)

        return scheme

    def validate_input(self, validation_definition):
        session_key   = validation_definition.metadata["session_key"]
        api_key       = validation_definition.parameters["api_key"]
        secret_key    = validation_definition.parameters["secret_key"]
        api_host      = validation_definition.parameters["api_host"]
        api_port      = validation_definition.parameters["api_port"]

        if secret_key == self.MASK:
            secret_key = self.get_password(session_key, api_key)
        try:
            if validation_definition.parameters["start_date"]:
                start_date = validation_definition.parameters["start_date"]
                validate.startdate(start_date)

            validate.halo_session(api_key, secret_key, api_host, api_port)
        except Exception as e:
            raise Exception, "Something did not go right: %s" % str(e)

    def encrypt_password(self, api_key, secret_key, session_key):
        args = {'token':session_key}
        service = client.connect(**args)

        try:
            # If the credential already exists, delte it.
            for storage_password in service.storage_passwords:
                if storage_password.username == api_key:
                    service.storage_passwords.delete(username=storage_password.username)
                    break

            # Create the credential.
            service.storage_passwords.create(secret_key, api_key)

        except Exception as e:
            raise Exception, "An error occurred updating credentials. Please ensure your user account has admin_all_objects and/or list_storage_passwords capabilities. Details: %s" % str(e)

    def mask_password(self, session_key, api_key, api_host, api_port, start_date):
        try:
            args = {'token':session_key}
            service = client.connect(**args)
            kind, input_name = self.input_name.split("://")
            item = service.inputs.__getitem__((input_name, kind))

            kwargs = {
                "api_key": api_key,
                "secret_key": self.MASK,
                "api_host": api_host,
                "api_port": api_port,
                "start_date": start_date
            }
            item.update(**kwargs).refresh()

        except Exception as e:
            raise Exception("Error updating inputs.conf: %s" % str(e))

    def get_password(self, session_key, api_key):
        args = {'token':session_key}
        service = client.connect(**args)

        # Retrieve the password from the storage/passwords endpoint
        for storage_password in service.storage_passwords:
            if storage_password.username == api_key:
                return storage_password.content.clear_password

    def send_arr_events(self, ew, input_name, state_store, events):
        for ev in events:
            event = Event()
            event.stanza = input_name
            event.data = json.dumps(ev)

            ew.write_event(event)
            state_store.update_state("created_at", ev['created_at'])

    def stream_events(self, inputs, ew):
        self.input_name, self.input_items = inputs.inputs.popitem()
        session_key = self._input_definition.metadata["session_key"]
        api_key     = self.input_items["api_key"]
        secret_key  = self.input_items['secret_key']
        api_host    = self.input_items['api_host']
        api_port    = self.input_items['api_port']
        event_id_exist = True
        first_batch = True
        self.USERNAME = api_key

        state_store = lib.FileStateStore(inputs.metadata, self.input_name)
        checkpoint = state_store.get_state("created_at")
        start_date = dateUtil.get_start_date(self.input_items, checkpoint)

        try:
            # If the password is not masked, mask it.
            if secret_key != self.MASK:
                self.encrypt_password(api_key, secret_key, session_key)
                self.mask_password(session_key, api_key, api_host, api_port, start_date)

            self.CLEAR_PASSWORD = self.get_password(session_key, api_key)
        except Exception as e:
            ew.log("ERROR", "Error: %s" % str(e))

        ew.log("INFO", "Starting from %s" % (start_date))

        e = lib.Event(api_key, self.CLEAR_PASSWORD, api_host, api_port, ew)

        end_date = start_date
        initial_event_id = e.latest_event("1", "", "1")["events"][0]["id"]
        while event_id_exist:
            try:
                batched = e.batch(end_date)
                start_date, end_date = e.loop_date(batched, end_date)
                if e.id_exists_check(batched, initial_event_id):
                    ew.log("INFO", "cphalo: detected initial event id match. Saving as final batch.")
                    event_id_exist = False

                if checkpoint and first_batch:
                    first_batch = False
                    batched.pop(0)

                if batched:
                    self.send_arr_events(ew, self.input_name, state_store, batched)
                    ew.log("INFO", "cphalo: saved events from %s to %s" % (start_date, end_date))
            except Exception as e:
                ew.log("ERROR", "Error: %s" % str(e))



if __name__ == "__main__":
    exitcode = MyScript().run(sys.argv)
    sys.exit(exitcode)