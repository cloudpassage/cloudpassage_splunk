"""Issue class"""

import cloudpassage.sanity as sanity
import cloudpassage.utility as utility
from cloudpassage.http_helper import HttpHelper


class Issue(object):
    """Initializing the Server class:

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
        """Returns a list of all issues.

        This query is limited to 20 pages of 100 items,
        totalling 2000 issues.

        Default filter returns only issues in the 'active' state.

        Keyword Args:
            server_id (list or str): A list or comma-separated string \
            containing server ids
            status (list or str): A list or comma-separated string \
            containing any of these: active, resolved
            since (str): Returns issues created since date in iso8601 format \
            such as: 2017-01-01
            until (str): Returns issues created until date in iso8601 format \
            such as 2017-01-01
            issue_type: (list or str): A list or comma-separated string \
            containing any of these: sva, csm, fim, lids, sam, fw, or agent
            group_id: (list or str): A list or comma-separated string \
            containing group ids
            critical: (list or str): A list or comma-separated string \
            containing any of these: true, false
            policy_id (list or str): A list or comma-separated string \
            containing policy ids
            os_type (list or str): A list or comma-separated string \
            containing any of these: Linux, Windows

         Returns:
            list: List of dictionary objects describing issues

        """

        session = self.session
        max_pages = 20
        key = "issues"
        endpoint = "/v1/issues"
        request = HttpHelper(session)
        params = utility.sanitize_url_params(kwargs)
        issues = request.get_paginated(endpoint, key,
                                       max_pages, params=params)
        return issues

    def describe(self, issue_id):
        """Get issue details by issue ID

        Args:
            issue_id (str): Issue ID

        Returns:
            dict: Dictionary object describing issue
        """

        endpoint = "/v1/issues/%s" % issue_id
        request = HttpHelper(self.session)
        response = request.get(endpoint)
        return response

    def resolve(self, issue_id):
        """Resolves an Issue.

        Args: issue_id (str): ID of issue to be altered

        Returns:
            True if successful, throws exception otherwise.

        """

        sanity.validate_object_id(issue_id)
        endpoint = "/v1/issues/%s" % issue_id
        response = None
        body = {"status": "resolved"}
        request = HttpHelper(self.session)
        response = request.put(endpoint, body)
        return response
