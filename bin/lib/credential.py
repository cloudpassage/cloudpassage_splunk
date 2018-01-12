"""credentialsFromSplunk.py
    Credentials Stored in Splunk Credentials Class file
"""


import os
import sys
import splunk.auth
import splunk.entity as entity


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

        return 'App:%s Username:%s Password:%s\r\n'% (self.app,self.username,self.password)

    def getPassword(self, sessionkey):

        if len(sessionkey) == 0:
            raise Exception, "No session key provided"
        if len(self.username) == 0:
            raise Exception, "No username provided"
        if len(self.app) == 0:
            raise Exception, "No app provided"

        try:
            entities = entity.getEntities(['admin', 'passwords'], namespace=self.app, owner='nobody', sessionKey=sessionkey)
        except Exception, e:
            raise Exception, "Could not get %s credentials from splunk. Error: %s" % (self.app, str(e))

        for i, c in entities.items():
            if (c['username'] == self.username):
                self.password = c['clear_password']
                return

        raise Exception, "No credentials have been found"

    def run(self):
        # sessionKey = sys.stdin.readline().strip()
        self.app = 'cloudpassage-splunk'
        self.username = 'mykey'
        sessionKey = splunk.auth.getSessionKey('admin','changeme')
        self.getPassword(sessionKey)
