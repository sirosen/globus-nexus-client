import logging

from globus_sdk.authorizers.base import GlobusAuthorizer

logger = logging.getLogger(__name__)


class LegacyGOAuthAuthorizer(GlobusAuthorizer):
    def __init__(self, legacy_token):
        logger.warn(("Setting up a LegacyGOAuthAuthorizer. It will use a "
                     "deprecated legacy token type."))
        logger.debug('Legacy token ends in "...{}" (last 5 chars)'
                     .format(legacy_token[-5:]))
        self.legacy_token = legacy_token
        self.header_val = "Globus-Goauthtoken {}".format(legacy_token)

    def set_authorization_header(self, header_dict):
        """
        Sets the ``Authorization`` header to
        "Globus-Goauthtoken <legacy_token>"
        """
        logger.debug(("Setting Globus-Goauthtoken Authorization Header: "
                      '"Globus-Goauthtoken ...{}" (last 5 chars)')
                     .format(self.header_val[-5:]))
        header_dict['Authorization'] = self.header_val
