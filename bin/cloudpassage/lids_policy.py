"""LidsPolicy class"""


from cloudpassage.policy import Policy


class LidsPolicy(Policy):
    """Initializing the LidsPolicy class:

    Args:
        session (:class:`cloudpassage.HaloSession`): \
        This will define how you interact \
        with the Halo API, including proxy settings and API keys \
        used for authentication.

    """

    policy = "lids_policy"
    policies = "lids_policies"

    @classmethod
    def endpoint(cls):
        """Defines endpoint for API requests"""
        return "/v1/%s" % LidsPolicy.policies

    @classmethod
    def pagination_key(cls):
        """Defines the pagination key for parsing paged results"""
        return LidsPolicy.policies

    @classmethod
    def policy_key(cls):
        """Defines the key used to pull the policy from the json document"""
        return LidsPolicy.policy
