import json
import time
import requests
import cloudpassage.utility as utility


class Retry(object):
    def __init__(self):
        self.max_retries = 5
        self.retry_delays = [2, 8, 15, 45, 90]
        self.success = False
        self.retries = 0

    def set_proxies(self, session, proxies):
        if proxies:
            session.proxies = proxies

    def get(self, url, headers, proxies, params=None):
        while self.retries < self.max_retries and not self.success:
            time.sleep(self.retry_delays[self.retries])
            self.retries += 1
            req = requests.session()
            self.set_proxies(req, proxies)

            if params:
                response = req.get(url, headers=headers, params=params)
            else:
                response = req.get(url, headers=headers)

            success, exception = utility.parse_status(url,
                                                      response.status_code,
                                                      response.text)

        return success, response, exception

    def put(self, url, headers, reqbody, proxies):
        while self.retries < self.max_retries and not self.success:
            time.sleep(self.max_retries[self.retries])
            self.retries += 1
            req = requests.session()
            self.set_proxies(req, proxies)

            response = req.put(url, headers=headers, data=json.dumps(reqbody))
            success, exception = utility.parse_status(url,
                                                      response.status_code,
                                                      response.text)

        return success, response, exception

    def post(self, url, headers, reqbody, proxies):
        while self.retries < self.max_retries and not self.success:
            time.sleep(self.retry_delays[self.retries])
            self.retries += 1
            req = requests.session()
            self.set_proxies(req, proxies)

            response = req.post(url, headers=headers, data=json.dumps(reqbody))
            success, exception = utility.parse_status(url,
                                                      response.status_code,
                                                      response.text)

        return success, response, exception

    def delete(self, url, headers, proxies):
        while self.retries < self.max_retries and not self.success:
            time.sleep(self.retry_delays[self.retries])
            self.retries += 1
            req = requests.session()
            self.set_proxies(req, proxies)

            response = req.delete(url, headers=headers)
            success, exception = utility.parse_status(url,
                                                      response.status_code,
                                                      response.text)
        return success, response, exception
