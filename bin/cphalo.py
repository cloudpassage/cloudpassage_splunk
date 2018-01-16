import os
import sys
import lib
import json
import xml.dom.minidom, xml.sax.saxutils
import splunklib.client as client
from splunklib.modularinput import *
import lib.validate as validate
import datetime


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

        startdate_arg = Argument(
            name="startdate",
            title="Starting Date",
            data_type=Argument.data_type_string,
            required_on_create=True,
            required_on_edit=True
        )
        scheme.add_argument(startdate_arg)

        return scheme

    def validate_input(self, validation_definition):
        session_key   = validation_definition.metadata["session_key"]
        api_key       = validation_definition.parameters["api_key"]
        secret_key    = validation_definition.parameters["secret_key"]
        api_host      = validation_definition.parameters["api_host"]
        startdate     = validation_definition.parameters["startdate"]
        api_port      = validation_definition.parameters["api_port"]

        try:
            validate.halo_session(api_key, secret_key, api_host, api_port)
            validate.startdate(startdate)
            pass
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

    def mask_password(self, session_key, api_key, api_host, api_port, startdate):
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
                "startdate": startdate
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

    def stream_events(self, inputs, ew):
        self.input_name, self.input_items = inputs.inputs.popitem()
        session_key = self._input_definition.metadata["session_key"]
        api_key     = self.input_items["api_key"]
        secret_key  = self.input_items['secret_key']
        api_host    = self.input_items['api_host']
        api_port    = self.input_items['api_port']
        startdate   = self.input_items["startdate"]
        self.USERNAME = api_key

        try:
            # If the password is not masked, mask it.
            if secret_key != self.MASK:
                self.encrypt_password(api_key, secret_key, session_key)
                self.mask_password(session_key, api_key, api_host, api_port, startdate)

            self.CLEAR_PASSWORD = self.get_password(session_key, api_key)
        except Exception as e:
            ew.log("ERROR", "Error: %s" % str(e))

        ew.log("INFO", "USERNAME:%s CLEAR_PASSWORD:%s" % (self.USERNAME, self.CLEAR_PASSWORD))
        e = lib.Event(api_key, self.CLEAR_PASSWORD)
        r = e.latest_event(1, '2018-01-01', 1)
        evStr = json.dumps(r)
        xmlStr = "<event><data>%s</data></event>" % xml.sax.saxutils.escape(evStr)

        event = Event()
        event.stanza = 'test1'
        event.data = xmlStr

        # Tell the EventWriter to write this event
        ew.write_event(event)
if __name__ == "__main__":
    exitcode = MyScript().run(sys.argv)
    sys.exit(exitcode)