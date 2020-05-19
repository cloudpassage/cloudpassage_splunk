import os
import sys
import lib
import json
import splunklib.client as client
import lib.validate as validate
import lib.date_util as dateUtil
import lib.proxy as proxy
from lib.logger import log

from splunklib.modularinput import *


class MyScript(Script):
    # Define some global variables
    MASK = "<nothing to see here>"
    APP = __file__.split(os.sep)[-3]
    USERNAME = None
    CLEAR_PASSWORD = None

    def get_scheme(self):
        scheme = Scheme("CloudPassage Splunk Connector")
        scheme.description = ("CloudPassage modular inputs")
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

        proxy_host_arg = Argument(
            name="proxy_host",
            title="Proxy Host",
            data_type=Argument.data_type_string,
            required_on_create=False,
            required_on_edit=False
        )
        scheme.add_argument(proxy_host_arg)

        proxy_port_arg = Argument(
            name="proxy_port",
            title="Proxy Port",
            data_type=Argument.data_type_string,
            required_on_create=False,
            required_on_edit=False
        )
        scheme.add_argument(proxy_port_arg)

        start_date_arg = Argument(
            name="start_date",
            title="Start Date. (If checkpoint exists, it will take precedence)",
            data_type=Argument.data_type_string,
            required_on_create=False,
            required_on_edit=False
        )
        scheme.add_argument(start_date_arg)

        per_page_arg = Argument(
            name="per_page",
            title="Number of events returned per Halo API call. (Max is 500)",
            data_type=Argument.data_type_number,
            required_on_create=True,
            required_on_edit=True
        )
        scheme.add_argument(per_page_arg)

        concurrency_arg = Argument(
            name="concurrency",
            title="API Concurrency",
            data_type=Argument.data_type_string,
            required_on_create=True,
            required_on_edit=True
        )
        scheme.add_argument(concurrency_arg)

        dedicated_log_arg = Argument(
            name="dedicated_log",
            title="Dedicated Log File Name (*.log)",
            data_type=Argument.data_type_string,
            required_on_create=True,
            required_on_edit=True
        )
        scheme.add_argument(dedicated_log_arg)

        return scheme

    def validate_input(self, validation_definition):
        session_key = validation_definition.metadata["session_key"]
        api_key = validation_definition.parameters["api_key"]
        secret_key = validation_definition.parameters["secret_key"]
        api_host = validation_definition.parameters["api_host"]
        per_page = validation_definition.parameters["per_page"]
        concurrency = validation_definition.parameters["concurrency"]
        dedicated_log = validation_definition.parameters["dedicated_log"]
        proxy_host = None
        proxy_port = None

        if secret_key == self.MASK:
            secret_key = self.get_password(session_key, api_key)
        try:
            if validation_definition.parameters["start_date"]:
                start_date = validation_definition.parameters["start_date"]
                validate.startdate(start_date)
            if validation_definition.parameters["proxy_host"]:
                proxy_host = validation_definition.parameters["proxy_host"]
            if validation_definition.parameters["proxy_port"]:
                proxy_port = validation_definition.parameters["proxy_port"]

            validate.halo_session(api_key, secret_key, api_host=api_host)
            validate.page_size(per_page)
            validate.dedicated_log_file_name(dedicated_log)
        except Exception as e:
            raise Exception, "Something did not go right: %s" % str(e)

    def encrypt_password(self, api_key, secret_key, session_key):
        args = {'token': session_key, 'app': self.APP}
        service = client.connect(**args)

        try:
            # If the credential already exists, delete it.
            for storage_password in service.storage_passwords:
                if storage_password.username == api_key:
                    service.storage_passwords.delete(username=storage_password.username)
                    break

            # Create the credential.
            service.storage_passwords.create(secret_key, api_key)

        except Exception as e:
            raise Exception, "An error occurred updating credentials. Please ensure your user account has admin_all_objects and/or list_storage_passwords capabilities. Details: %s" % str(
                e)

    def mask_password(self, input_name, session_key, api_key, api_host, \
                      proxy_host, proxy_port, start_date, per_page, concurrency, dedicated_log):
        try:
            args = {'token': session_key, 'app': self.APP}
            service = client.connect(**args)
            kind, name = input_name.split("://")
            item = service.inputs.__getitem__((name, kind))

            kwargs = {
                "api_key": api_key,
                "secret_key": self.MASK,
                "api_host": api_host,
                "proxy_host": proxy_host,
                "proxy_port": proxy_port,
                "start_date": start_date,
                "per_page": per_page,
                "concurrency": concurrency,
                "dedicated_log": dedicated_log,
            }
            item.update(**kwargs).refresh()

        except Exception as e:
            raise Exception("Error updating inputs.conf: %s" % str(e))

    def get_password(self, session_key, api_key):
        args = {'token': session_key, 'app': self.APP}
        service = client.connect(**args)

        # Retrieve the password from the storage/passwords endpoint
        for storage_password in service.storage_passwords:
            if storage_password.username == api_key:
                return storage_password.content.clear_password

    def send_arr_events(self, ew, input_name, checkpoint_name, state_store, events):
        for ev in events:
            event = Event()
            event.stanza = input_name
            event.data = json.dumps(ev)

            ew.write_event(event)
            state_store.update_state(checkpoint_name, ev['created_at'])

    def stream_events(self, inputs, ew):
        for input_name, input_item in inputs.inputs.iteritems():
            ew.log("INFO", "Starting with %s" % (input_name))
            session_key = self._input_definition.metadata["session_key"]

            api_key = input_item["api_key"]
            secret_key = input_item['secret_key']
            api_host = input_item['api_host']
            per_page = input_item['per_page']
            concurrency = int(input_item['concurrency'])
            dedicated_log = input_item['dedicated_log']
            event_id_exist = True
            first_batch = True
            self.USERNAME = api_key

            ew.log("INFO", "Starting with %s" % (input_name))
            log.INFO("API key - %s" % (api_key), dedicated_log)
            log.INFO("Secret Key - %s" % (secret_key), dedicated_log)
            log.INFO("API host - %s" % (api_host), dedicated_log)
            log.INFO("Per Page - %s" % (per_page), dedicated_log)
            log.INFO("CONCURRENCY - %s" % (concurrency), dedicated_log)
            log.INFO("Dedicated log file - %s" % (dedicated_log), dedicated_log)
            log.INFO("Event ID list - %s" % (event_id_exist), dedicated_log)
            log.INFO("First Batch - %s" % (first_batch), dedicated_log)

            try:
                proxy_host = input_item['proxy_host']
            except:
                proxy_host = None
            try:
                proxy_port = input_item['proxy_port']
            except:
                proxy_port = None

            if validate.optional_proxy_values(proxy_host, proxy_port):
                ew.log("INFO", "Setting proxy values %s:%s" % (proxy_host, proxy_port))
                log.INFO("Setting proxy values %s:%s" % (proxy_host, proxy_port), dedicated_log)
                proxy.set_https_proxy(proxy_host, proxy_port)

            state_store = lib.FileStateStore(inputs.metadata, input_name)
            kind, checkpoint_name = input_name.split("://")
            log.INFO("Kind - %s" % (kind), dedicated_log)
            log.INFO("Checkpoint name - %s" % (checkpoint_name), dedicated_log)
            checkpoint = state_store.get_state(checkpoint_name)
            start_date = dateUtil.get_start_date(input_item, checkpoint)
            log.INFO("Start date - %s" % (start_date), dedicated_log)

            try:
                # If the password is not masked, mask it.
                if secret_key != self.MASK:
                    self.encrypt_password(api_key, secret_key, session_key)
                    self.mask_password(input_name, session_key,
                                       api_key, api_host,
                                       proxy_host, proxy_port,
                                       start_date, per_page)

                self.CLEAR_PASSWORD = self.get_password(session_key, api_key)
            except Exception as e:
                ew.log("ERROR", "Error: %s" % str(e))
                log.INFO("ERROR", "Error: %s" % str(e), dedicated_log)

            ew.log("INFO", "%s Starting from %s with page size = %s" % (input_name, start_date, per_page))
            log.INFO("%s Starting from %s with page size = %s" % (input_name, start_date, per_page), dedicated_log)

            e = lib.Event(api_key, self.CLEAR_PASSWORD, api_host, per_page=per_page)
            end_date = start_date
            log.INFO("End date - %s" % (end_date), dedicated_log)

            try:
                initial_event_id = e.latest_event()["events"][0]["id"]
                while event_id_exist:
                    log.INFO("Inside While statement ~~~~~~~~~~~~~~~~~", dedicated_log)
                    batched = e.batch(end_date)
                    start_date, end_date = e.loop_date(batched, end_date)
                    log.INFO("start date - %s ------ end date - %s" % (start_date, end_date), dedicated_log)
                    if e.id_exists_check(batched, initial_event_id):
                        ew.log("INFO",
                               "cphalo: %s detected initial event id match. Saving as final batch." % (input_name))
                        log.INFO("cphalo: %s detected initial event id match. Saving as final batch." % (input_name))
                        event_id_exist = False

                    if checkpoint and first_batch:
                        first_batch = False
                        batched.pop(0)

                    if batched:
                        self.send_arr_events(ew, input_name, checkpoint_name, state_store, batched)
                        ew.log("INFO", "cphalo: %s saved events from %s to %s" % (input_name, start_date, end_date))
                        log.INFO("cphalo: %s saved events from %s to %s" % (input_name, start_date, end_date))
            except Exception as e:
                ew.log("ERROR", "Error: %s" % str(e))
                log("Error: %s" % str(e), dedicated_log)


if __name__ == "__main__":
    exitcode = MyScript().run(sys.argv)
    sys.exit(exitcode)