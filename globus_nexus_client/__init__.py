import logging

from globus_nexus_client.client import NexusClient

__all__ = ['NexusClient']


# configure logging for a library, per python best practices:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
# NB: this won't work on py2.6 because `logging.NullHandler` wasn't added yet
logging.getLogger('globus_nexus_client').addHandler(logging.NullHandler())
