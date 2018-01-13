"""credentialsFromSplunk.py
    Credentials Stored in Splunk Credentials Class file
"""


import os
import sys
import json
import splunk.entity as entity
import splunk.Intersplunk


class Credential(object):
    """ Credential object:
        Attributes:

            app: the Splunk app storing the credential
            realm: the system needing the credential
            username: the username for the credential
            password: the credential's password or key

        access the credentials in /servicesNS/nobody/<myapp>/storage/passwords
    """

    def __init__(self):
        self.password = ""
        self.run()

    def __str__(self):
        """Function Override: Print credential object
        """

        return 'App:%s Username:%s Password:%s\r\n SessionKey:%s'% (self.app,self.username, self.password, self.sessionKey)

    def getPassword(self):

        if len(self.sessionKey) == 0:
            raise Exception, "No session key provided"
        if len(self.username) == 0:
            raise Exception, "No username provided"
        if len(self.app) == 0:
            raise Exception, "No app provided"

        try:
            entities = entity.getEntities(['admin', 'passwords'], namespace=self.app, owner='nobody', sessionKey=self.sessionKey)
        except Exception, e:
            raise Exception, "Could not get %s credentials from splunk. Error: %s" % (self.app, str(e))

        for i, c in entities.items():
            if (c['username'] == self.username):
                self.password = c['clear_password']
                return

        raise Exception, "No credentials have been found"

    def find_between(self, s, first, last ):
        try:
            start = s.index( first ) + len( first )
            end = s.index( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def find_between_r(self, s, first, last ):
        try:
            start = s.rindex( first ) + len( first )
            end = s.rindex( last, start )
            return s[start:end]
        except ValueError:
            return ""

    def run(self):
        results,dummy,settings = splunk.Intersplunk.getOrganizedResults()
        if settings:
            s = str(settings)
            self.find_between(s, "<session_key>", "</session_key>" )
            self.sessionKey = self.find_between_r(s, "<session_key>", "</session_key>")
            self.app = 'cloudpassage'
            self.username = 'mykey'
            self.getPassword()
