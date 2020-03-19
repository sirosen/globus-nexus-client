#!/usr/bin/env python3
"""
Example script which takes username, password, and group ID, then lists all group member
identity IDs.

Prompts are printed to stderr, so it can be used in a quick pipeline like
  ./list_group_members.py | xargs globus get-identities --jmespath 'identities[].email'
"""
import getpass
import sys

from globus_sdk import BasicAuthorizer

from globus_nexus_client import LegacyGOAuthAuthorizer, NexusClient


def main():
    print("Globus ID Username: ", file=sys.stderr, end="")
    username = input()
    password = getpass.getpass("Password: ")
    print("Globus Group ID: ", file=sys.stderr, end="")
    group_id = input()
    basic_auth = BasicAuthorizer(username, password)
    basic_auth_client = NexusClient(authorizer=basic_auth)
    token = basic_auth_client.get_goauth_token()
    client = NexusClient(authorizer=LegacyGOAuthAuthorizer(token))
    for member in client.get_group_memberships(group_id)["members"]:
        print(member["identity_id"])


if __name__ == "__main__":
    main()
