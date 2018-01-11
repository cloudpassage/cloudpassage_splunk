# import splunk.entity as entity

# # access the credentials in /servicesNS/nobody/app_name/admin/passwords
# def getCredentials(sessionKey):
#    myapp = 'cp_test'
#    try:
#       # list all credentials
#       entities = entity.getEntities(['admin', 'changeme'], namespace=myapp,
#                                     owner='nobody', sessionKey=sessionKey)
#    except Exception, e:
#       raise Exception("Could not get %s credentials from splunk. Error: %s"
#                       % (myapp, str(e)))

#    # return first set of credentials
#    for i, c in entities.items():
#         return c['username'], c['clear_password']

#    raise Exception("No credentials have been found")

# def main():
#     # read session key sent from splunkd
#     sessionKey = sys.stdin.readline().strip()

#     if len(sessionKey) == 0:
#        sys.stderr.write("Did not receive a session key from splunkd. " +
#                         "Please enable passAuth in inputs.conf for this " +
#                         "script\n")
#        exit(2)

#     # now get twitter credentials - might exit if no creds are available
#     username, password = getCredentials(sessionKey)
#     # use the credentials to access the data source

import splunk.entity as entity
import splunk.auth, splunk.search

def getCredentials(sessionKey):
    myapp = 'cloudpassage_splunk'
    try:
        # list all credentials
        entities = entity.getEntities(
            ['admin', 'passwords'], namespace=myapp,
            owner='nobody', sessionKey=sessionKey)
        print entities.items()
    except Exception, e:
        raise Exception(
            "Could not get %s credentials from splunk."
            "Error: %s" % (myapp, str(e)))
    credentials = []
    # return credentials
    for i, c in entities.items():
        print c
        credentials.append((c['username'], c['clear_password']))
    return credentials
    raise Exception("No credentials have been found")

sessionKey = splunk.auth.getSessionKey('admin','changeme')
credentials = getCredentials(sessionKey)
print credentials
# for username, password in credentials:
#     print username
#     print password