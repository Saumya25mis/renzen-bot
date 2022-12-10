# pylint: disable=invalid-name, no-else-raise, no-else-return, line-too-long

"""Get discord secrets."""

# Use this code snippet in your app..
# If you need more information about configurations or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developers/getting-started/python/

import base64
import json
import logging
import os
from typing import Any

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_secret(secret_name: str) -> Any:
    """Get discord secrets."""
    logger.info("Retrieving secrets...")

    region_name = "us-west-1"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name="secretsmanager", region_name=region_name)

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        if e.response["Error"]["Code"] == "DecryptionFailureException":
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InternalServiceErrorException":
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidParameterException":
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "InvalidRequestException":
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response["Error"]["Code"] == "ResourceNotFoundException":
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if "SecretString" in get_secret_value_response:
            secret = get_secret_value_response["SecretString"]

        else:
            secret = base64.b64decode(get_secret_value_response["SecretBinary"])

    # Your code goes here.
    return secret
    # return json.loads(secret)


ENV = os.getenv("CURRENT_ENVIRONMENT")

TOKEN = get_secret(f"{ENV}-DiscordToken")

DB_INFO = json.loads(get_secret(f"{ENV}-DBPassword"))

DB_PASSWORD = DB_INFO["password"]
DB_USERNAME = DB_INFO["username"]
DB_PORT = DB_INFO["port"]
DB_ENDPOINT = DB_INFO["host"]
