"""FirewallPolicy, FirewallRule, FirewallService, FirewallZone,
and FirewallInterface classes
"""

import cloudpassage.sanity as sanity
from cloudpassage.http_helper import HttpHelper
from cloudpassage.policy import Policy


class FirewallPolicy(Policy):
    """Initializing the FirewallPolicy class:

    Args:
        session (HaloSession): This will define how you interact \
        with the Halo API, including proxy settings and API keys \
        used for authentication.

    """

    policy = "firewall_policy"
    policies = "firewall_policies"

    @classmethod
    def endpoint(cls):
        """Defines endpoint for API requests"""
        return "/v1/%s" % FirewallPolicy.policies

    @classmethod
    def pagination_key(cls):
        """Defines the pagination key for parsing paged results"""
        return FirewallPolicy.policies

    @classmethod
    def policy_key(cls):
        """Defines the key used to pull the policy from the json document"""
        return FirewallPolicy.policy


class FirewallRule(object):
    """Initializing the FirewallRule class:

    Args:
        session (:class:`cloudpassage.HaloSession`): \
        This will define how you interact \
        with the Halo API, including proxy settings and API keys \
        used for authentication.

    """

    def __init__(self, session):
        self.session = session
        return None

    def list_all(self, firewall_policy_id):
        """List all rules associated with a firewall policy.

        Args:
            firewall_policy_id (str): ID of firewall policy

        Returns:
            list: Returns a list of rules associated with the firewall \
            policy, each of which are represented by an object of type dict.

        """

        request = HttpHelper(self.session)
        endpoint = ("/v1/firewall_policies/%s/firewall_rules/" %
                    firewall_policy_id)
        key = "firewall_rules"
        max_pages = 30
        response = request.get_paginated(endpoint, key, max_pages)
        return response

    def describe(self, firewall_policy_id, firewall_rule_id):
        """Get the detailed configuration of a firewall rule

        Args:
            firewall_policy_id (str): ID of the policy to retrieve \
            detailed configuration information for
            firewall_rule_id (str): ID of the specific rule to \
            retrieve details for

        Returns:
            dict: dictionary object representing the entire \
            firewall rule

        """

        request = HttpHelper(self.session)
        endpoint = ("/v1/firewall_policies/%s/firewall_rules/%s" %
                    (firewall_policy_id, firewall_rule_id))
        response = request.get(endpoint)
        result = response["firewall_rule"]
        return result

    def create(self, firewall_policy_id, rule_body):
        """Creates a rule within a firewall policy.

        Args:
            rule_body (dict or str): string or dict containing the json \
            representation of the firewall policy to be created.

        Returns:
            str: ID of newly-created firewall rule


        Example rule_body:

        ::

          {
            "firewall_rule" : {
              "chain": "INPUT",
              "active": true,
              "firewall_interface": "7b881ca072b1012ec681404096c01709",
              "firewall_service": "7b6409a072b1012ec681404096c01709",
              "connection_states": "NEW, ESTABLISHED",
              "action": "ACCEPT",
              "log": true,
              "log_prefix": "East-3 input-accept",
              "comment": "All servers in group East-3 must include this rule",
              "position": 4
              }
          }

        """

        sanity.validate_object_id(firewall_policy_id)
        request = HttpHelper(self.session)
        endpoint = ("/v1/firewall_policies/%s/firewall_rules" %
                    firewall_policy_id)
        response = request.post(endpoint, rule_body)
        policy_id = response["firewall_rule"]["id"]
        return policy_id

    def delete(self, firewall_policy_id, firewall_rule_id):
        """Delete a firewall policy rule

        Args:
            firewall_policy_id (str): ID of firewall policy containing\
            the rule to be deleted
            firewall_rule_id (str): ID of firewall policy rule to delete

        Returns:
            None if successful.  Errors will throw exceptions.

        """

        sanity.validate_object_id([firewall_policy_id, firewall_rule_id])
        request = HttpHelper(self.session)
        endpoint = ("/v1/firewall_policies/%s/firewall_rules/%s" %
                    (firewall_policy_id, firewall_rule_id))
        request.delete(endpoint)
        return None

    def update(self, firewall_policy_id, firewall_rule_id, firewall_rule_body):
        """Update a firewall policy rule.

        Args:
            firewall_policy_id (str): ID of firewall policy containing the\
            rule to be modified.
            firewall_rule_id (str): ID of firewall policy rule to modify.
            firewall_rule_body (dict or str): String- or dictionary-type \
            object containing the fields to be updated within the firewall \
            rule.

        Returns:
            None if successful.  Errors will throw exceptions.

        Example:

        ::

          {
            "firewall_rule" : {
              "chain": "INPUT",
              "active": true,
              "firewall_interface": "7b881ca072b1012ec681404096c01709",
              "firewall_service": "7b6409a072b1012ec681404096c01709",
              "connection_states": "NEW, ESTABLISHED",
              "action": "ACCEPT",
              "log": true,
              "log_prefix": "East-3 input-accept",
              "comment": "All servers in group East-3 must include this rule",
              "position": 4
              }
          }

        """

        sanity.validate_object_id([firewall_policy_id, firewall_rule_id])
        request = HttpHelper(self.session)
        endpoint = ("/v1/firewall_policies/%s/firewall_rules/%s" %
                    (firewall_policy_id, firewall_rule_id))
        request.put(endpoint, firewall_rule_body)
        return None


class FirewallZone(Policy):
    """Initializing the FirewallZone class:

    Args:
        session (:class:`cloudpassage.HaloSession`): \
        This will define how you interact \
        with the Halo API, including proxy settings and API keys \
        used for authentication.

    """

    policy = "firewall_zone"
    policies = "firewall_zones"

    @classmethod
    def endpoint(cls):
        """Defines endpoint for API requests"""
        return "/v1/%s" % FirewallZone.policies

    @classmethod
    def pagination_key(cls):
        """Defines the pagination key for parsing paged results"""
        return FirewallZone.policies

    @classmethod
    def policy_key(cls):
        """Defines the key used to pull the policy from the json document"""
        return FirewallZone.policy


class FirewallService(Policy):
    """Initializing the FirewallService class:

    Args:
        session (:class:`cloudpassage.HaloSession`): \
        This will define how you interact \
        with the Halo API, including proxy settings and API keys \
        used for authentication.

    """

    policy = "firewall_service"
    policies = "firewall_services"

    @classmethod
    def endpoint(cls):
        """Defines endpoint for API requests"""
        return "/v1/%s" % FirewallService.policies

    @classmethod
    def pagination_key(cls):
        """Defines the pagination key for parsing paged results"""
        return FirewallService.policies

    @classmethod
    def policy_key(cls):
        """Defines the key used to pull the policy from the json document"""
        return FirewallService.policy


class FirewallInterface(Policy):
    """Initializing the FirewallInterface class:

    Args:
        session (:class:`cloudpassage.HaloSession`): \
        This will define how you interact \
        with the Halo API, including proxy settings and API keys \
        used for authentication.

    """

    policy = "firewall_interface"
    policies = "firewall_interfaces"

    @classmethod
    def endpoint(cls):
        """Defines endpoint for API requests"""
        return "/v1/%s" % FirewallInterface.policies

    @classmethod
    def pagination_key(cls):
        """Defines the pagination key for parsing paged results"""
        return FirewallInterface.policies

    @classmethod
    def policy_key(cls):
        """Defines the key used to pull the policy from the json document"""
        return FirewallInterface.policy
