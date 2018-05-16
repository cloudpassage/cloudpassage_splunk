import os


def set_https_proxy(proxy_host, proxy_port):
    os.environ['HTTPS_PROXY'] = "%s:%s" % (proxy_host, proxy_port)
    return os.environ['HTTPS_PROXY']
