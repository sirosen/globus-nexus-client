import six

from globus_sdk import (
    AccessTokenAuthorizer, RefreshTokenAuthorizer, BasicAuthorizer,
    NullAuthorizer, exc)
from globus_sdk.base import BaseClient, merge_params

from globus_nexus_client.goauth_authorizer import LegacyGOAuthAuthorizer
from globus_nexus_client.response import GlobusArrayResponse


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
        self._headers['Content-Type'] = 'application/json'

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
        if not isinstance(self.authorizer, LegacyGOAuthAuthorizer):
            raise exc.GlobusError('get_user() requires LegacyGOAuthAuthorizer '
                                  'based authorization (a.k.a. Nexus Tokens)')
        self.logger.info("NexusClient.get_user({})".format(username))
        return self.get('/users/{}'.format(username))

    def get_user_groups_profile(self, group_id, username):
        """
        :rtype: GlobusResponse
        """
        self.logger.info(
            "NexusClient.get_user_profile({}, {})".format(group_id, username))
        return self.get(
            '/groups/{}/members/{}/user'.format(group_id, username))

    def get_group(self, group_id):
        """
        :rtype: GlobusResponse
        """
        self.logger.info("NexusClient.get_group({})".format(group_id))
        return self.get('/groups/{}'.format(group_id))

    def create_group(self, name, description, **params):
        """
        :rtype: GlobusResponse
        """
        merge_params(params, name=name, description=description)
        self.logger.info("NexusClient.create_group({})".format(params))
        return self.post('/groups', json_body=params)

    def update_group(self, group_id, group_doc):
        """
        :rtype: GlobusResponse
        """
        self.logger.info("NexusClient.update_group({})".format(group_id))
        return self.put('/groups/{}'.format(group_id), json_body=group_doc)

    def delete_group(self, group_id):
        """
        :rtype: GlobusResponse
        """
        self.logger.info("NexusClient.delete_group({})".format(group_id))
        return self.delete('/groups/{}'.format(group_id))

    def list_groups(self, for_all_identities=None,
                    include_identity_set_params=None,
                    fields=None, my_roles=None, **params):
        """
        :rtype: GlobusResponse
        """
        # if not string, assume iterable
        if my_roles and not isinstance(my_roles, six.string_types):
            my_roles = ",".join(my_roles)

        merge_params(params, for_all_identities=for_all_identities,
                     include_identity_set_params=include_identity_set_params,
                     fields=fields, my_roles=my_roles)
        self.logger.info("NexusClient.list_groups({})".format(str(params)))
        return self.get('/groups', params=params,
                        response_class=GlobusArrayResponse)

    def get_group_tree(self, group_id, depth=None, my_roles=None,
                       my_statuses=None, **params):
        # if not string, assume iterable
        if my_roles and not isinstance(my_roles, six.string_types):
            my_roles = ",".join(my_roles)
        # if not string, assume iterable
        if my_statuses and not isinstance(my_statuses, six.string_types):
            my_statuses = ",".join(my_statuses)

        merge_params(params, depth=depth, my_roles=my_roles,
                     my_statuses=my_statuses)
        self.logger.info("NexusClient.get_group_tree({},{})"
                         .format(group_id, str(params)))
        return self.get('/groups/{}/tree'.format(group_id), params=params,
                        response_class=GlobusArrayResponse)

    def get_group_memberships(self, group_id):
        """
        :rtype: GlobusResponse
        """
        self.logger.info("NexusClient.get_group_members({})".format(group_id))
        return self.get('/groups/{}/members'.format(group_id),
                        response_class=GlobusArrayResponse)

    def get_group_membership(self, group_id, username):
        """
        :rtype: GlobusResponse
        """
        self.logger.info("NexusClient.get_group_membership({}, {})"
                         .format(group_id, username))
        return self.get('/groups/{}/members/{}'.format(group_id, username))

    def create_group_memberships(self, group_id, usernames, emails=None,
                                 **params):
        """
        :rtype: GlobusResponse
        """
        if isinstance(usernames, six.string_types):
            usernames = [usernames]
        if isinstance(emails, six.string_types):
            emails = [emails]
        body = {'users': list(usernames)}
        if emails:
            body['emails'] = list(emails)

        self.logger.info("NexusClient.create_group_memberships({}, {})"
                         .format(group_id, usernames))
        return self.post('/groups/{}/members'.format(group_id),
                         json_body=body)

    def update_group_membership(self, group_id, username, membership_doc,
                                **params):
        """
        :rtype: GlobusResponse
        """
        self.logger.info("NexusClient.update_group_membership({})"
                         .format(membership_doc))
        return self.put('/groups/{}/members/{}'.format(group_id, username),
                        body=membership_doc)
