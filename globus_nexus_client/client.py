from globus_sdk import config
from globus_sdk.exc import GlobusError
from globus_sdk.base import BaseClient


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
    AUTHTYPE_GOAUTH_TOKEN = "goauth_token"

    def __init__(self, environment=config.get_default_environ(), token=None,
                 app_name=None):
        BaseClient.__init__(self, "nexus", environment, token=token,
                            app_name=app_name)

    def config_load_token(self):
        return config._get_token('nexus_token', self.environment)

    def set_token(self, token):
        """
        Overrides default method, which would set a token as a Bearer token.
        We need to set it to the custom Globus-Goauthtoken Authentication type.
        """
        self.auth_type = self.AUTHTYPE_GOAUTH_TOKEN
        self._headers['Authorization'] = 'Globus-Goauthtoken {}'.format(token)

    def get_goauth_token(self, username, password):
        """
        Note that these tokens have a long lifetime and should be
        saved and re-used.

        :rtype: string
        """
        self.set_auth_basic(username, password)
        r = self.get('/goauth/token?grant_type=client_credentials')
        try:
            return r['access_token']
        except KeyError:
            raise GlobusError(r)
        else:
            raise

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

    def list_groups(self):
        """
        :rtype: GlobusResponse
        """
        return self.get('/groups/list')
