Disclaimer: This Is Not An Official Globus.org Product
======================================================

This is a personal project for talking to the Globus Nexus API with all of the
benefits of the Globus SDK.
It is not a Globus maintained product.

If you don't know what that is, stop reading here and go away.
Otherwise, this will hopefully alleviate the pains of trying to use Nexus.


Globus Nexus Client
===================

When Globus added the new `SDK <https://github.com/globus/globus-sdk-python>`_
it did not include functionality for the Nexus API.

This package contains a client for talking to Nexus, based on the same core
client model provided by the SDK.
You should therefore think of this as a third-party extension to the SDK for
talking to Nexus.

Importing and Usage
-------------------

.. warning::

    Because this is not part of the SDK, you don't get at it with a simple
    ``from globus_sdk import NexusClient``.

Instead, imports come from the package namespace::

    from globus_nexus_client import NexusClient

You can then use ``NexusClient`` methods as usual.

The client object supports all of the typical Authorizers that the SDK
provides, and this package provides an additional Authorizer for using
Nexus-issued tokens::

    from globus_nexus_client import NexusClient, LegacyGOAuthAuthorizer

    client = NexusClient(authorizer=LegacyGOAuthAuthorizer('<nexus token>'))

Documentation
-------------

There is no web doc or other maintained documentation for this project, but
there are docstrings on all methods of the client object. Either browse the
source or use ``help()`` in the python REPL.
