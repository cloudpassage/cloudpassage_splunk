import multiprocessing
import copy_reg
import types
import datetime
import os
import signal
import re
import json
from functools import partial
import settings as settings
import cloudpassage


def _pickle_method(message):
    if message.im_self is None:
        return getattr, (message.im_class, message.im_func.func_name)
    else:
        return getattr, (message.im_self, message.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)


class Event(object):
    """Initializing Event

        Args:
        key_id: Halo API key_id
        secret_key: Halo API secret key
    """

    def __init__(self, key_id, secret_key, api_host, **kwargs):
        self.event_id_exist = True
        self.api_host = api_host
        self.api_port = 443
        self.key_id = key_id
        self.secret_key = secret_key
        self.session = self.create_halo_session_object()
        self.per_page = kwargs["per_page"]
        self.integration_string = self.get_integration_string()

    def create_halo_session_object(self):
        session = cloudpassage.HaloSession(self.key_id,
                                           self.secret_key,
                                           api_host=self.api_host,
                                           integration_string=self.integration_string)
        return session

    def get(self, date, page):
        """HTTP GET events from Halo"""

        api = cloudpassage.HttpHelper(self.session)
        url = "/v1/events?per_page=%s&page=%s&since=%s" % (self.per_page,
                                                           page,
                                                           date)
        return api.get(url)

    def latest_event(self):
        """get the latest event from Halo"""

        api = cloudpassage.HttpHelper(self.session)
        url = "/v1/events?sort_by=created_at.desc&per_page=1&page=1"
        return api.get(url)

    def interrupt_handler(self, signum, frame):
        """interruptHandler"""

        print "Beginning shutdown..."

    def init_worker(self):
        """init_worker"""

        signal.signal(signal.SIGINT, self.interrupt_handler)

    def batch(self, date):
        """multiprocessing to get all the events"""
        batched = []
        paginations = list(range(1, settings.pagination_limit() + 1))

        try:
            for page in paginations:
                data = self.get(date, page)
                batched.extend(data["events"])
            return batched
        except KeyboardInterrupt:
            print "Caught KeyboardInterrupt, terminating workers"

    def historical_limit_date(self):
        """get historical_limit_date (90 days)"""

        historical_limit = settings.historical_limit()
        temp = (datetime.datetime.now() - datetime.timedelta(days=historical_limit))
        date = temp.strftime('%Y-%m-%d')
        return date

    def sort_by(self, data, param):
        """ sorting the events data"""

        sort_data = sorted(data, key=lambda x: x[param])
        return sort_data

    def get_end_date(self, dates, end_date):
        """find the end date of each events batch"""

        if end_date != self.historical_limit_date:
            return dates[-1]["created_at"]
        date_obj = cputils.strToDate(dates[-1]["created_at"])
        return date_obj.strftime('%Y-%m-%d')

    def id_exists_check(self, data, event_id):
        """check event id exist"""
        return any(k['id'] == event_id for k in data)

    def loop_date(self, batched, end_date):
        """grab starting date for the next event batch"""

        sorted_data = self.sort_by(batched, "created_at")
        start_date = sorted_data[0]["created_at"]
        end_date = self.get_end_date(sorted_data, end_date)
        return start_date, end_date

    def get_integration_string(self):
        """Return integration string for this tool."""
        return "cloudpassage_splunk/%s" % self.get_tool_version()

    def get_tool_version(self):
        """Get version of this tool from the __init__.py file."""
        here_path = os.path.abspath(os.path.dirname(__file__))
        init_file = os.path.join(here_path, "__init__.py")
        ver = 0
        with open(init_file, 'r') as i_f:
            rx_compiled = re.compile(r"\s*__version__\s*=\s*\"(\S+)\"")
            ver = rx_compiled.search(i_f.read()).group(1)
        return ver