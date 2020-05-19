from __future__ import print_function
from builtins import str
import sys, os, datetime

def log(msg, file_name):
    f = open(os.path.join(os.environ["SPLUNK_HOME"], "var", "log", "splunk", file_name), "a")
    print(str(datetime.datetime.now().isoformat()), msg, file=f)
    f.close()
