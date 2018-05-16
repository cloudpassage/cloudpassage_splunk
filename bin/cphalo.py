import os
import sys
import lib
import json
import splunklib.client as client
import lib.validate as validate
import lib.date_util as dateUtil
import lib.proxy as proxy

from splunklib.modularinput import *

class MyScript(Script):
    # Define some global variables
    MASK           = "<nothing to see here>"
    APP            = __file__.split(os.sep)[-3]
    USERNAME       = None
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

        return scheme

    def validate_input(self, validation_definition):
        session_key   = validation_definition.metadata["session_key"]
        api_key       = validation_definition.parameters["api_key"]
        secret_key    = validation_definition.parameters["secret_key"]
        api_host      = validation_definition.parameters["api_host"]
        per_page      = validation_definition.parameters["per_page"]
        proxy_host    = None
        proxy_port    = None

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
            raise Exception, "An error occurred updating credentials. Please ensure your user account has admin_all_objects and/or list_storage_passwords capabilities. Details: %s" % str(e)

    def mask_password(self, input_name, session_key, api_key, api_host, proxy_host, proxy_port, start_date, per_page):
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
                "per_page": per_page
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

    def stream_events(self, inputs, ew):
        for input_name, input_item in inputs.inputs.iteritems():
            ew.log("INFO", "Starting with %s" % (input_name))
            session_key = self._input_definition.metadata["session_key"]
            api_key     = input_item["api_key"]
            secret_key  = input_item['secret_key']
            api_host    = input_item['api_host']
            per_page    = input_item['per_page']
            self.USERNAME = api_key

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
                proxy.set_https_proxy(proxy_host, proxy_port)

            state_store = lib.FileStateStore(inputs.metadata, input_name)
            kind, checkpoint_name = input_name.split("://")
            checkpoint = state_store.get_state(checkpoint_name)
            start_date = dateUtil.get_start_date(input_item, checkpoint)

            try:
                if secret_key != self.MASK:
                    self.encrypt_password(api_key, secret_key, session_key)
                    self.mask_password(input_name, session_key,
                                       api_key, api_host,
                                       proxy_host, proxy_port,
                                       start_date, per_page)

                self.CLEAR_PASSWORD = self.get_password(session_key, api_key)
            except Exception as e:
                ew.log("ERROR", "Error: %s" % str(e))

            event = lib.EventController(api_key, self.CLEAR_PASSWORD, api_host, per_page=per_page)
            ew.log("INFO", "%s Starting from %s with page size = %s" % (input_name, start_date, per_page))
            event.perform(start_date, checkpoint, input_name, checkpoint_name, state_store)

if __name__ == "__main__":
    exitcode = MyScript().run(sys.argv)
    sys.exit(exitcode)
