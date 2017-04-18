from globus_sdk import (
    AccessTokenAuthorizer, RefreshTokenAuthorizer, BasicAuthorizer,
    NullAuthorizer, exc)
from globus_sdk.base import BaseClient, merge_params

from globus_nexus_client.goauth_authorizer import LegacyGOAuthAuthorizer


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
                                BasicAuthorizer, NullAuthorizer,
                                LegacyGOAuthAuthorizer]

    def __init__(self, legacy_token=None, **kwargs):
        authorizer = kwargs.pop('authorizer', None)
        if legacy_token:
            authorizer = LegacyGOAuthAuthorizer(legacy_token)
        BaseClient.__init__(self, "nexus", authorizer=authorizer, **kwargs)

    def get_goauth_token(self):
        """
        Note that these tokens have a long lifetime and should be
        saved and re-used.

        :rtype: string
        """
        self.logger.info("NexusClient.get_goauth_token() called")
        if not isinstance(self.authorizer, BasicAuthorizer):
            raise exc.GlobusError('get_goauth_token() requires basic auth')
        r = self.get('/goauth/token?grant_type=client_credentials')
        try:
            tok = r['access_token']
            self.logger.debug("NexusClient.get_goauth_token() success")
            return tok
        except KeyError:
            self.logger.warn(
                ("NexusClient.get_goauth_token() failed somehow, raising an "
                 "exception now"))
            raise exc.GlobusAPIError(r)

    def get_user(self, username):
        """
        :rtype: GlobusResponse
        """
        self.logger.info("NexusClient.get_user({})".format(username))
        return self.get('/users/{}'.format(username))

    def get_group(self, group_id):
        """
        :rtype: GlobusResponse
        """
        self.logger.info("NexusClient.get_group({})".format(group_id))
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
        self.logger.info("NexusClient.list_groups({})".format(str(params)))
        return self.get('/groups', params=params)

    def get_group_tree(self, group_id, depth=None, my_roles=None,
                       my_statuses=None, **params):
        merge_params(params, depth=depth, my_roles=my_roles,
                     my_statuses=my_statuses)
        self.logger.info("NexusClient.get_group_tree({},{})"
                         .format(group_id, str(params)))
        return self.get('/groups/{}/tree'.format(group_id), params=params)
