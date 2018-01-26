import sys
from os import path
sys.path.append(path.dirname( path.dirname( path.abspath(__file__) ) ) )

import cloudpassage
import datetime
import re


def halo_session(api_key, secret_key, api_host=None, **kwargs):
    session = cloudpassage.HaloSession(api_key, secret_key,
                                       api_host=api_host,
                                       api_port=443,
                                       proxy_host=kwargs['proxy_host'],
                                       proxy_port=kwargs['proxy_port'])
    api = cloudpassage.HttpHelper(session)
    try:
        api.get('/v1/servers?per_page=1')
    except Exception as e :
        raise Exception, e
    return True

def validate_time(date):
    """validate time"""
    iso_regex = "\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{1,6})?(Z|[+-]\d{4})?)?$"
    m = re.match(iso_regex, date)
    try:
        filter(None, re.match(iso_regex, date).groups())
    except AttributeError as e:
        raise ValueError(date + " is not in iso8601 time format")

def validate_time_range(date):
    """validate time range"""
    date_parsed = None
    time_range = datetime.datetime.now() - datetime.timedelta(days=90)
    try:
        date_parsed = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ" )
    except:
        date_parsed = datetime.datetime.strptime(date, '%Y-%m-%d')

    if date_parsed < time_range:
        raise ValueError(date + " is out of 90 days data retention range")

def startdate(date):
    validate_time(date)
    validate_time_range(date)
    return True

