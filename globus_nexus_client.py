import logging

from globus_sdk import BaseClient, GlobusHTTPResponse, exc
from globus_sdk.authorizers import BasicAuthorizer, StaticGlobusAuthorizer
from globus_sdk.transport import RequestsTransport

log = logging.getLogger(__name__)

ACTIVE_IDENTITY_HEADER = "X-Globus-Active-Identity"


class _NexusTransport(RequestsTransport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._active_identity = None

    @property
    def _headers(self):
        h = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if self._active_identity is not None:
            h[ACTIVE_IDENTITY_HEADER] = self._active_identity
        return h


class NexusArrayResponse(GlobusHTTPResponse):
    """
    super-simple response class for data where the top-level JSON entity is an
    Array, so __iter__ can be defined naturally on that array
    """

    def __iter__(self):
        return iter(self.data)


class LegacyGOAuthAuthorizer(StaticGlobusAuthorizer):
    def __init__(self, legacy_token):
        self.header_val = f"Globus-Goauthtoken {legacy_token}"


class NexusClient(BaseClient):
    """
    Client for Globus Nexus API.

    Basic usage should be something similar to

    >>> import getpass
    >>> from globus_nexus_client import NexusClient
    >>> from globus_sdk import BasicAuthorizer
    >>> nc = NexusClient(authorizer=BasicAuthorizer("username", getpass.getpass()))

    followed by whatever actions you want to perform using basic auth, e.g.

    >>> from globus_nexus_client import LegacyGOAuthAuthorizer
    >>> token = nc.get_goauth_token()
    >>> nc2 = NexusClient(authorizer=LegacyGOAuthAuthorizer(token))

    Alternatively, you can use Globus Auth tokens with Nexus Client, as in

    >>> from globus_nexus_client import NexusClient
    >>> from globus_sdk import AccessTokenAuthorizer
    >>> nc = NexusClient(authorizer=AccessTokenAuthorizer(my_access_token))
    """

    service_name = "nexus"
    transport_class = _NexusTransport

    def __init__(self, legacy_token=None, **kwargs):
        authorizer = kwargs.pop("authorizer", None)
        if legacy_token:
            authorizer = LegacyGOAuthAuthorizer(legacy_token)
        super().__init__(authorizer=authorizer, **kwargs)

    @property
    def active_identity(self):
        return self.transport._active_identity

    @active_identity.setter
    def active_identity(self, val):
        self.transport._active_identity = val

    def get_goauth_token(self) -> str:
        """
        Note that these tokens have a long lifetime and should be
        saved and re-used.
        """
        log.debug("NexusClient.get_goauth_token() called")
        if not isinstance(self.authorizer, BasicAuthorizer):
            raise exc.GlobusError("get_goauth_token() requires basic auth")
        r = self.get("/goauth/token?grant_type=client_credentials")
        try:
            tok = r["access_token"]
            log.debug("NexusClient.get_goauth_token() success")
            return tok
        except KeyError:
            log.warn(
                "NexusClient.get_goauth_token() failed somehow, raising an "
                "exception now"
            )
            raise exc.GlobusAPIError(r)

    def get_user(self, username: str) -> GlobusHTTPResponse:
        if not isinstance(self.authorizer, LegacyGOAuthAuthorizer):
            raise exc.GlobusError(
                "get_user() requires LegacyGOAuthAuthorizer "
                "based authorization (a.k.a. Nexus Tokens)"
            )
        log.debug(f"NexusClient.get_user({username})")
        return self.get(f"/users/{username}")

    def get_user_groups_profile(self, group_id, username) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.get_user_profile({group_id}, {username})")
        return self.get(f"/groups/{group_id}/members/{username}/user")

    def get_group(self, group_id) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.get_group({group_id})")
        return self.get(f"/groups/{group_id}")

    def create_group(self, name: str, description: str, **params) -> GlobusHTTPResponse:
        params["name"] = name
        params["description"] = description
        log.debug(f"NexusClient.create_group({params})")
        return self.post("/groups", data=params)

    def update_group(self, group_id, group_doc) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.update_group({group_id})")
        return self.put(f"/groups/{group_id}", data=group_doc)

    def delete_group(self, group_id) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.delete_group({group_id})")
        return self.delete(f"/groups/{group_id}")

    def list_groups(
        self, for_all_identities=None, fields=None, my_roles=None, **params
    ) -> GlobusHTTPResponse:
        # if not string, assume iterable
        if my_roles and not isinstance(my_roles, str):
            my_roles = ",".join(my_roles)

        # either string "true" (lowercase) or None (remove from params)
        for_all_identities = "true" if for_all_identities else None

        if for_all_identities is not None:
            params["for_all_identities"] = for_all_identities
        if fields is not None:
            params["fields"] = fields
        if my_roles is not None:
            params["my_roles"] = my_roles
        log.debug("NexusClient.list_groups({})".format(str(params)))
        return NexusArrayResponse(self.get("/groups", params=params))

    def get_group_tree(
        self, group_id, depth=None, my_roles=None, my_statuses=None, **params
    ) -> GlobusHTTPResponse:
        # if not string, assume iterable
        if my_roles and not isinstance(my_roles, str):
            my_roles = ",".join(my_roles)
        # if not string, assume iterable
        if my_statuses and not isinstance(my_statuses, str):
            my_statuses = ",".join(my_statuses)

        if depth is not None:
            params["depth"] = depth
        if my_roles is not None:
            params["my_roles"] = my_roles
        if my_statuses is not None:
            params["my_statuses"] = my_statuses
        log.debug("NexusClient.get_group_tree({},{})".format(group_id, str(params)))
        return NexusArrayResponse(self.get(f"/groups/{group_id}/tree", params=params))

    def get_group_memberships(self, group_id) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.get_group_members({group_id})")
        return NexusArrayResponse(self.get(f"/groups/{group_id}/members"))

    def get_group_membership(self, group_id, username: str) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.get_group_membership({group_id}, {username})")
        return self.get(f"/groups/{group_id}/members/{username}")

    def create_group_memberships(
        self, group_id, usernames, emails=None, **params
    ) -> GlobusHTTPResponse:
        if isinstance(usernames, str):
            usernames = [usernames]
        if isinstance(emails, str):
            emails = [emails]
        body = {"users": list(usernames)}
        if emails:
            body["emails"] = list(emails)

        log.debug(f"NexusClient.create_group_memberships({group_id}, {usernames})")
        return self.post(f"/groups/{group_id}/members", data=body)

    def update_group_membership(
        self, group_id, username: str, membership_doc, **params
    ) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.update_group_membership({membership_doc})")
        return self.put(f"/groups/{group_id}/members/{username}", data=membership_doc)
