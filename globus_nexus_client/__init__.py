import logging
import typing as t

from globus_sdk import BaseClient, GlobusHTTPResponse, exc
from globus_sdk.authorizers import BasicAuthorizer, StaticGlobusAuthorizer

log = logging.getLogger(__name__)

ACTIVE_IDENTITY_HEADER = "X-Globus-Active-Identity"


class NexusArrayResponse(GlobusHTTPResponse):
    """
    super-simple response class for data where the top-level JSON entity is an
    Array, so __iter__ can be defined naturally on that array
    """

    def __iter__(self):
        return iter(self.data)


class LegacyGOAuthAuthorizer(StaticGlobusAuthorizer):
    def __init__(self, legacy_token: str):
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

    def __init__(self, legacy_token: t.Optional[str] = None, **kwargs):
        self._active_identity: t.Optional[str] = None
        authorizer = kwargs.pop("authorizer", None)
        if legacy_token:
            authorizer = LegacyGOAuthAuthorizer(legacy_token)
        super().__init__(authorizer=authorizer, **kwargs)

    @property
    def active_identity(self) -> t.Optional[str]:
        return self._active_identity

    @active_identity.setter
    def active_identity(self, val: t.Optional[str]):
        self._active_identity = val

    def request(self, *args, headers=None, **kwargs) -> GlobusHTTPResponse:
        headers = headers or {}
        if self._active_identity is not None:
            headers[ACTIVE_IDENTITY_HEADER] = self._active_identity
        headers["Content-Type"] = "application/json"
        return super().request(*args, headers=headers, **kwargs)

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

    def get_user_groups_profile(
        self, group_id: str, username: str
    ) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.get_user_profile({group_id}, {username})")
        return self.get(f"/groups/{group_id}/members/{username}/user")

    def get_group(self, group_id: str) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.get_group({group_id})")
        return self.get(f"/groups/{group_id}")

    def create_group(
        self,
        name: str,
        description: str,
        body_params: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> GlobusHTTPResponse:
        body_params = body_params or {}
        body_params["name"] = name
        body_params["description"] = description
        log.debug("NexusClient.create_group(%s)", body_params)
        return self.post("/groups", data=body_params)

    def update_group(
        self, group_id: str, group_doc: t.Dict[str, t.Any]
    ) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.update_group({group_id})")
        return self.put(f"/groups/{group_id}", data=group_doc)

    def delete_group(self, group_id: str) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.delete_group({group_id})")
        return self.delete(f"/groups/{group_id}")

    def list_groups(
        self,
        for_all_identities: t.Optional[bool] = None,
        fields: t.Optional[str] = None,
        my_roles: t.Union[None, str, t.List[str]] = None,
        my_statuses: t.Optional[str] = None,
        query_params: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> NexusArrayResponse:
        query_params = query_params or {}

        # if not string, assume iterable
        if my_roles is not None and not isinstance(my_roles, str):
            my_roles = ",".join(my_roles)
        # if not string, assume iterable
        if my_statuses is not None and not isinstance(my_statuses, str):
            my_statuses = ",".join(my_statuses)

        # either string "true" (lowercase) or None (remove from params)
        for_all_identities_ = "true" if for_all_identities else None

        if for_all_identities_ is not None:
            query_params["for_all_identities"] = for_all_identities_
        if fields is not None:
            query_params["fields"] = fields
        if my_roles is not None:
            query_params["my_roles"] = my_roles
        if my_statuses is not None:
            query_params["my_statuses"] = my_statuses
        log.debug("NexusClient.list_groups(%s)", query_params)
        return NexusArrayResponse(self.get("/groups", query_params=query_params))

    def get_group_tree(
        self,
        group_id: str,
        depth: t.Optional[int] = None,
        my_roles: t.Union[None, str, t.List[str]] = None,
        my_statuses: t.Union[None, str, t.List[str]] = None,
        query_params: t.Optional[t.Dict[str, t.Any]] = None,
    ) -> NexusArrayResponse:
        query_params = query_params or {}

        # if not string, assume iterable
        if my_roles is not None and not isinstance(my_roles, str):
            my_roles = ",".join(my_roles)
        # if not string, assume iterable
        if my_statuses is not None and not isinstance(my_statuses, str):
            my_statuses = ",".join(my_statuses)

        if depth is not None:
            query_params["depth"] = depth
        if my_roles is not None:
            query_params["my_roles"] = my_roles
        if my_statuses is not None:
            query_params["my_statuses"] = my_statuses
        log.debug("NexusClient.get_group_tree(%s,%s)", group_id, query_params)
        return NexusArrayResponse(
            self.get(f"/groups/{group_id}/tree", query_params=query_params)
        )

    def get_group_memberships(self, group_id: str) -> NexusArrayResponse:
        log.debug(f"NexusClient.get_group_members({group_id})")
        return NexusArrayResponse(self.get(f"/groups/{group_id}/members"))

    def get_group_membership(self, group_id: str, username: str) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.get_group_membership({group_id}, {username})")
        return self.get(f"/groups/{group_id}/members/{username}")

    def create_group_memberships(
        self,
        group_id: str,
        usernames: t.Sequence[str],
        emails: t.Optional[t.Sequence[str]] = None,
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
        self, group_id: str, username: str, membership_doc: t.Dict[str, t.Any]
    ) -> GlobusHTTPResponse:
        log.debug(f"NexusClient.update_group_membership({membership_doc})")
        return self.put(f"/groups/{group_id}/members/{username}", data=membership_doc)
