from globus_sdk import (
    AccessTokenAuthorizer, RefreshTokenAuthorizer, BasicAuthorizer,
    exc)
from globus_sdk.base import BaseClient, merge_params


class NexusClient(BaseClient):
    """
    Client for Globus Nexus API.

    Basic usage should be something similar to

    >>> import getpass
    >>> from globus_nexus_client import NexusClient
    >>> nc = NexusClient()
    >>> nc.set_token(nc.get_goauth_token('username', getpass.getpass()))

    followed by whatever actions you want to perform.
    If you want to save a token to disk, put it in ``~/.globus.cfg`` in
    ``nexus_token`` (under the ``[general]`` heading, like ``auth_token`` and
    ``transfer_token``).
    """
    allowed_authorizer_types = [AccessTokenAuthorizer, RefreshTokenAuthorizer,
                                BasicAuthorizer]

    def __init__(self, **kwargs):
        BaseClient.__init__(self, "nexus", **kwargs)

    def get_goauth_token(self):
        """
        Note that these tokens have a long lifetime and should be
        saved and re-used.

        :rtype: string
        """
        if not isinstance(self.authorizer, BasicAuthorizer):
            raise exc.GlobusError('get_goauth_token() requires basic auth')
        r = self.get('/goauth/token?grant_type=client_credentials')
        try:
            return r['access_token']
        except KeyError:
            raise exc.GlobusAPIError(r)

    def get_user(self, username):
        """
        :rtype: GlobusResponse
        """
        return self.get('/users/{}'.format(username))

    def get_group(self, group_id):
        """
        :rtype: GlobusResponse
        """
        return self.get('/groups/{}'.format(group_id))

    def list_groups(self, for_all_identities=None,
                    include_identity_set_params=None,
                    fields=None, my_roles=None, **params):
        """
        :rtype: GlobusResponse
        """
        merge_params(params, for_all_identities=for_all_identities,
                     include_identity_set_params=include_identity_set_params,
                     fields=fields, my_roles=my_roles)
        return self.get('/groups/list', json_body=params)
