"""Policy class"""

import cloudpassage.sanity as sanity
import cloudpassage.utility as utility
from cloudpassage.http_helper import HttpHelper


class Policy(object):
    """Base class inherited by other specific policy classes."""

    def __init__(self, session):
        self.session = session
        self.max_pages = 30

    @classmethod
    def endpoint(cls):
        """Not implemented at this level.  Raises exception."""
        raise NotImplementedError

    @classmethod
    def pagination_key(cls):
        """Not implemented at this level.  Raises exception."""
        raise NotImplementedError

    @classmethod
    def policy_key(cls):
        """Not implemented at this level.  Raises exception."""
        raise NotImplementedError

    def list_all(self):
        """Lists all policies of this type.

        Returns:
            list: List of policies (represented as dictionary-type objects)

        Note:
            This query is limited to 30 pages.

        """

        request = HttpHelper(self.session)
        return request.get_paginated(self.endpoint(), self.pagination_key(),
                                     self.max_pages)

    def describe(self, policy_id):
        """Get the detailed configuration of a policy

        Args:
            policy_id (str): ID of the policy to retrieve \
            detailed configuration information for

        Returns:
            dict: dictionary object representing the entire, detailed, policy

        """

        request = HttpHelper(self.session)
        describe_endpoint = "%s/%s" % (self.endpoint(), policy_id)
        return request.get(describe_endpoint)[self.policy_key()]

    def create(self, policy_body):
        """Creates a policy from JSON document.

        Returns the ID of the new policy
        """

        request = HttpHelper(self.session)
        request_body = utility.policy_to_dict(policy_body)
        return request.post(self.endpoint(),
                            request_body)[self.policy_key()]["id"]

    def delete(self, policy_id):
        """Delete a policy by ID.  Success returns None"""

        sanity.validate_object_id(policy_id)
        request = HttpHelper(self.session)
        delete_endpoint = "%s/%s" % (self.endpoint(), policy_id)
        request.delete(delete_endpoint)
        return None

    def update(self, policy_body):
        """Update a policy.  Success returns None"""

        request = HttpHelper(self.session)
        request_body = utility.policy_to_dict(policy_body)
        policy_id = request_body[self.policy_key()]["id"]
        sanity.validate_object_id(policy_id)
        update_endpoint = "%s/%s" % (self.endpoint(), policy_id)
        request.put(update_endpoint, request_body)
        return None
