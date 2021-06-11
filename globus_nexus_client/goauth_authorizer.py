from globus_sdk.authorizers import StaticGlobusAuthorizer


class LegacyGOAuthAuthorizer(StaticGlobusAuthorizer):
    def __init__(self, legacy_token):
        self.header_val = f"Globus-Goauthtoken {legacy_token}"
