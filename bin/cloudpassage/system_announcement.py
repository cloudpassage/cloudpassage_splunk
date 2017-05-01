"""SyetemAnnouncement class"""


from cloudpassage.http_helper import HttpHelper


class SystemAnnouncement(object):
    """Initializing the SystemAnnouncement class:

    Args:
        session (:class:`cloudpassage.HaloSession`): \
        This will define how you interact \
        with the Halo API, including proxy settings and API keys \
        used for authentication.

    """

    module_name = "system_announcements"

    def __init__(self, session):
        self.session = session

        return None

    @classmethod
    def build_endpoint(cls):
        """Defines endpoint for API requests"""
        return "/v1/%s" % SystemAnnouncement.module_name

    def list_all(self):
        """Returns a list of all system announcements
        """

        session = self.session
        endpoint = self.build_endpoint()
        request = HttpHelper(session)
        response = request.get(endpoint)
        announcement_list = response["announcements"]
        return announcement_list
