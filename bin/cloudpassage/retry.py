import json
import time
import requests
import cloudpassage.utility as utility


class Retry(object):
    def __init__(self):
        self.max_retries = 50
        self.retry_delay = 60
        self.success = False
        self.retries = 0

    def delay(self):
        time.sleep(self.retry_delay)

    def get(self, url, headers, params=None):
        while self.retries < self.max_retries and not self.success:
            self.delay()
            self.retries += 1
            req = requests.session()

            if params:
                response = req.get(url, headers=headers, params=params)
            else:
                response = req.get(url, headers=headers)

            success, exception = utility.parse_status(url,
                                                      response.status_code,
                                                      response.text)

        return success, response, exception

    def put(self, url, headers, reqbody):
        while self.retries < self.max_retries and not self.success:
            self.delay()
            self.retries += 1
            req = requests.session()

            response = req.put(url, headers=headers, data=json.dumps(reqbody))
            success, exception = utility.parse_status(url,
                                                      response.status_code,
                                                      response.text)

        return success, response, exception

    def post(self, url, headers, reqbody):
        while self.retries < self.max_retries and not self.success:
            self.delay()
            self.retries += 1
            req = requests.session()

            response = req.post(url, headers=headers, data=json.dumps(reqbody))
            success, exception = utility.parse_status(url,
                                                      response.status_code,
                                                      response.text)

        return success, response, exception

    def delete(self, url, headers):
        while self.retries < self.max_retries and not self.success:
            self.delay()
            self.retries += 1
            req = requests.session()

            response = req.delete(url, headers=headers)
            success, exception = utility.parse_status(url,
                                                      response.status_code,
                                                      response.text)
        return success, response, exception
