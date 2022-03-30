import base64

import boto3

from meadowrun.aws_integration.ec2_alloc import _get_account_number
from meadowrun.aws_integration.management_lambdas.ec2_alloc_stub import (
    ignore_boto3_error_code,
)
from meadowrun.credentials import UsernamePassword


def get_username_password(region_name: str) -> UsernamePassword:
    """
    Returns (username, password) for the ECR default repository. Can be passed to
    functions in docker_controller.py
    """
    client = boto3.client("ecr", region_name=region_name)
    response = client.get_authorization_token()
    username_password = base64.b64decode(
        response["authorizationData"][0]["authorizationToken"]
    ).decode("utf-8")
    username, sep, password = username_password.partition(":")
    if not sep or not password:
        raise ValueError(
            "username_password was not in expected format username:password"
        )

    return UsernamePassword(username, password)


def ensure_repository(repository: str, region_name: str) -> str:
    """
    Takes a "simple" repository name like "foo", creates it if it doesn't exist and
    returns the repository name that can be used with the docker API. Returns e.g.
    012345678901.dkr.ecr.us-east-2.amazonaws.com/foo
    """
    client = boto3.client("ecr", region_name=region_name)
    ignore_boto3_error_code(
        lambda: client.create_repository(repositoryName=repository),
        "RepositoryAlreadyExistsException",
    )
    return f"{_get_account_number()}.dkr.ecr.{region_name}.amazonaws.com"


def does_image_exist(repository: str, tag: str, region_name: str) -> bool:
    """
    Returns whether the specified image exists.

    It feels like you should be able to just see whether docker_controller:pull_image is
    successful, but that takes significantly longer, and you also don't know if a
    failure is the result of something else like an authentication issue.
    """
    client = boto3.client("ecr", region_name=region_name)
    success, result = ignore_boto3_error_code(
        lambda: client.describe_images(
            repositoryName=repository, imageIds=[{"imageTag": tag}]
        ),
        "ImageNotFoundException",
    )
    return success