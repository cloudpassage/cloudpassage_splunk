"""LocalUserGroup Class"""

import cloudpassage.utility as utility
from cloudpassage.http_helper import HttpHelper


class LocalUserGroup(object):
    """Initializing the LocalUserGroup class:

    Args:
        session (:class:`cloudpassage.HaloSession`): \
        This will define how you interact \
        with the Halo API, including proxy settings and API keys \
        used for authentication.

    """

    def __init__(self, session):
        self.session = session
        return None

    def list_all(self, **kwargs):
        """Return a list of all local user groups.

        This will only return a maximum of 50 pages, which amounts
        to 500 local user groups.

        Keyword Args:
            group_id (list or str): A list of local user groups \
            in the according server group
            server_id (list or str): A list of local user groups \
            in the according server
            os_type (list or str): A list of local user groups \
            in the according os type
            name (list or str): A list of local user groups \
            with the according name
            memebers (list or str): A list of local user groups \
            with the according members
            comment (str):  A list of local user groups \
            with the according comment
            member_name (list or str): A list of local user groups \
            with the according member names
            server_name (list or str): A list of local user groups \
            with the according server name
            server_label (list or str): A list of local user groups \
            with the according server label
            gid (list or str): A list of local user groups \
            with the according gid
            sid (list or str): A list of local user groups \
            with the according sid

        Returns:
            list: List of dictionary objects describing local user groups

        """
        endpoint = "/v1/local_groups"
        key = "local_groups"
        max_pages = 50
        request = HttpHelper(self.session)
        params = utility.sanitize_url_params(kwargs)
        response = request.get_paginated(endpoint, key,
                                         max_pages, params=params)
        return response

    def describe(self, server_id, gid):
        """Get local user group deatils by server id and gid

        Args:
            server_id = Server ID
            gid = gid

        Returns:
            list: List of dictionary object describing local user group detail

        """
        endpoint = "/v1/local_groups?server_id=%s&gid=%s" % (server_id,
                                                             gid)
        request = HttpHelper(self.session)
        response = request.get(endpoint)
        group_detail = response["local_groups"]
        return group_detail
