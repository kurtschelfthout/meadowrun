"""
Credentials can be managed in a few different ways. Let's say we have a
username/password that we need to access a Docker container registry. The simplest thing
to do is for the user to send the username/password to the coordinator, which then sends
it to workers when the coordinator assigns them a job that needs it. Alternatively, we
could just send over the secret if the worker actually needs it, i.e. the image is not
in the worker machine's local cache.

It's probably better for the user to send over a credentials source, e.g. an AWS secret
or even just a file path that is restricted in some way. If the user is accessing the
coordinator over the public internet, this makes it possible to avoid sending the
username/password over the public internet (even if it's encrypted). Also, this makes it
possible to rotate secrets without manually updating the coordinator. If we take this
strategy, then we need to decide whether the coordinator should send over the actual
credentials or the credentials source to the workers. Sending the actual credentials
exposes them over the wire (even if they're encrypted), but sending the credentials
source means that all of the workers need direct access to the secrets. If e.g. an AWS
IAM role is used to restrict access to an AWS secret, then this is not good because the
job then gets full access to that AWS secret.

TODO actually encrypt the credentials as we send them over?
"""

import pickle
from typing import Union, Literal

from meadowgrid.meadowgrid_pb2 import ServerAvailableFile


# Represents a way to get credentials. Kind of silly right now, but we should be
# adding more types soon.
CredentialsSource = Union[ServerAvailableFile]
# Represents a service that credentials can be used for. A little silly right now, but
# we should be adding more soon
CredentialsService = Literal["DOCKER"]


def get_credentials_from_source(source: CredentialsSource) -> bytes:
    if isinstance(source, ServerAvailableFile):
        with open(source.path, "r") as f:
            lines = f.readlines()
        if len(lines) != 2:
            raise ValueError(
                "ServerAvailableFile for credentials must have exactly two lines, one "
                "for username, and one for password"
            )
        # strip just the trailing newlines, other whitespace might be needed
        lines = [l.rstrip("\r\n") for l in lines]
        # TODO ideally we would use the pickle version that the remote job can accept
        return pickle.dumps((lines[0], lines[1]))
    else:
        raise ValueError(f"Unknown type of credentials source {type(source)}")
