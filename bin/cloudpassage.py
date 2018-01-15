#!/usr/bin/env python
#
# Copyright 2013 Splunk, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"): you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import random, sys
import lib
import json
import xml.dom.minidom, xml.sax.saxutils

from splunklib.modularinput import *

class MyScript(Script):
    """All modular inputs should inherit from the abstract base class Script
    from splunklib.modularinput.script.
    They must override the get_scheme and stream_events functions, and,
    if the scheme returned by get_scheme has Scheme.use_external_validation
    set to True, the validate_input function.
    """
    def get_scheme(self):
        """When Splunk starts, it looks for all the modular inputs defined by
        its configuration, and tries to run them with the argument --scheme.
        Splunkd expects the modular inputs to print a description of the
        input in XML on stdout. The modular input framework takes care of all
        the details of formatting XML and printing it. The user need only
        override get_scheme and return a new Scheme object.

        :return: scheme, a Scheme object
        """
        # "cloudpassage" is the name Splunk will display to users for this input.
        scheme = Scheme("cloudpassage")

        scheme.description = "Streams events from cloudpassage"
        scheme.use_external_validation = True
        scheme.use_single_instance = True

        key_argument = Argument("key_id")
        key_argument.title = "Api Key id"
        key_argument.data_type = Argument.data_type_string
        key_argument.description = "Api Key ID"
        key_argument.required_on_create = True
        scheme.add_argument(key_argument)

        secret_argument = Argument("secret_key")
        secret_argument.title = "Api Secret key"
        secret_argument.data_type = Argument.data_type_string
        secret_argument.description = "Api secret key"
        secret_argument.required_on_create = True
        scheme.add_argument(secret_argument)

        return scheme

    def validate_input(self, validation_definition):
        """If validate_input does not raise an Exception, the input is
        assumed to be valid. Otherwise it prints the exception as an error message
        when telling splunkd that the configuration is invalid.

        When using external validation, after splunkd calls the modular input with
        --scheme to get a scheme, it calls it again with --validate-arguments for
        each instance of the modular input in its configuration files, feeding XML
        on stdin to the modular input to do validation. It is called the same way
        whenever a modular input's configuration is edited.

        :param validation_definition: a ValidationDefinition object
        """
        # Get the parameters from the ValidationDefinition object,
        key_id = validation_definition.parameters["key_id"]
        secret_key = validation_definition.parameters["secret_key"]

        if not key_id or not secret_key:
            raise ValueError("key id or secret_key is empty")

    def stream_events(self, inputs, ew):
        """This function handles all the action: splunk calls this modular input
        without arguments, streams XML describing the inputs to stdin, and waits
        for XML on stdout describing events.

        If you set use_single_instance to True on the scheme in get_scheme, it
        will pass all the instances of this input to a single instance of this
        script.

        :param inputs: an InputDefinition object
        :param ew: an EventWriter object
        """
        # Go through each input for this modular input
        for input_name, input_item in inputs.inputs.iteritems():
            # Get the values, cast them as floats
            key_id = input_item["key_id"]
            secret_key = input_item["secret_key"]

        # Create an Event object, and set its data fields
        e = lib.Event(key_id, secret_key)
        r = e.latest_event(1, '2018-01-01', 1)
        evStr = json.dumps(r)
        xmlStr = "<event><data>%s</data></event>" % xml.sax.saxutils.escape(evStr)

        event = Event()
        event.stanza = 'test1'
        event.data = xmlStr

        # Tell the EventWriter to write this event
        ew.write_event(event)

if __name__ == "__main__":
    sys.exit(MyScript().run(sys.argv))
