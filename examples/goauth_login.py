#!/usr/bin/env python3
"""
This is a sample usage of globus_nexus_client to do a GlobusID login and get a new
GOAuth token (legacy token)

It then uses that token to build a LegacyGOAuthAuthorizer and get user information
"""
import getpass

from globus_sdk import BasicAuthorizer

from globus_nexus_client import LegacyGOAuthAuthorizer, NexusClient


def main():
    username = input("Globus ID Username: ")
    password = getpass.getpass("Password: ")
    basic_auth = BasicAuthorizer(username, password)
    basic_auth_client = NexusClient(authorizer=basic_auth)
    token = basic_auth_client.get_goauth_token()
    client = NexusClient(authorizer=LegacyGOAuthAuthorizer(token))
    print(client.get_user(username))


if __name__ == "__main__":
    main()
