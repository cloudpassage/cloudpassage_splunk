import os
import re


class ConfigHelper(object):
    def __init__(self):
        self.ua = ConfigHelper.get_ua_string()
        self.product_version = ConfigHelper.get_product_version()

    @classmethod
    def get_ua_string(cls):
        product = "HaloSplunkEventConnector"
        version = ConfigHelper.get_product_version()
        ua_string = product + "/" + version
        return ua_string

    @classmethod
    def get_product_version(cls):
        init = open(os.path.join(os.path.dirname(__file__),
                    "__init__.py")).read()
        rx_compiled = re.compile(r"\s*__version__\s*=\s*\"(\S+)\"")
        version = rx_compiled.search(init).group(1)
        return version