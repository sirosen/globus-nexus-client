import logging

from globus_nexus_client.client import NexusClient
from globus_nexus_client.goauth_authorizer import LegacyGOAuthAuthorizer

__all__ = ["NexusClient", "LegacyGOAuthAuthorizer"]


# configure logging for a library, per python best practices:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger("globus_nexus_client").addHandler(logging.NullHandler())
