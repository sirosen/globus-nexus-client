Disclaimer: This Is Not An Official Globus.org Product
======================================================

This is a personal project borne of my own frustration trying to interact with
the Globus Nexus API.
It is not a Globus maintained product.

If you don't know what that is, stop reading here and go away.
Otherwise, this will hopefully alleviate the pains of trying to use the
unsupported ``python-nexus-client`` sample lib, which is remarkably terrible.


Globus Nexus Client
===================

When Globus added the new `SDK <https://github.com/globus/globus-sdk-python>`_
it did not include functionality for the old Nexus API.

This package contains a client for talking to Nexus, based on the same core
client model provided by the SDK.
You should therefore think of this as a third-party extension to the SDK for
talking to Nexus.

Importing and Usage
-------------------

Because this is not part of the SDK, you don't get at it with a simple
``from globus_sdk import NexusClient``.

Instead, imports come from the package namespace::

    from globus_nexus_client import NexusClient

You can then use ``NexusClient`` methods as usual.
