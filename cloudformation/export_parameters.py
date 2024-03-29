# pylint:disable=invalid-name, line-too-long, broad-except, f-string-without-interpolation
"""Uploads cloudformation files to s3, calls stacks.

Updates environments cloudformation from the production (main) and staging branches.
"""
# from typing import List
import json
import os

import boto3

# import botocore.exceptions

CODE_ENVIRONMENT = os.getenv("CURRENT_ENVIRONMENT")
CODE_BUILD_NUMBER = os.getenv("CODEBUILD_BUILD_NUMBER")


# GENERATE STACK UPDATE PARAMETERS
client = boto3.client("cloudformation")

stack_summary = client.describe_stacks(StackName=f"{CODE_ENVIRONMENT}deploy")["Stacks"]

# get parameters:
# CodeEnvironment
# BuildSpecLocation:
# GitHubBranchName
# GitHubRepoName
# HostedZoneId
# AlertsChannelID
parameters = stack_summary[0]["Parameters"]

parameters_json = {k["ParameterKey"]: k["ParameterValue"] for k in parameters}

# Secrets
session = boto3.session.Session()
client = session.client(service_name="secretsmanager")

secret = client.get_secret_value(SecretId=f"{CODE_ENVIRONMENT}-DiscordToken")[
    "SecretString"
]
parameters_json.update({"DiscordToken": secret})

secret = client.get_secret_value(SecretId=f"{CODE_ENVIRONMENT}-JwtSecret")[
    "SecretString"
]
parameters_json.update({"JwtSecret": secret})

secret = client.get_secret_value(
    SecretId=f"{CODE_ENVIRONMENT}-GithubOauthClientSecret"
)["SecretString"]
parameters_json.update({"GithubOauthClientSecret": secret})


output_json = {"Parameters": parameters_json}

with open("STACK_PARAMETERS.json", "a") as f:  # pylint:disable=unspecified-encoding
    f.write(json.dumps(output_json))


# get secrets

# if CODE_ENVIRONMENT == "production":
#     # update all environments terraform
#     pass
# elif CODE_ENVIRONMENT == "staging":
#     # update all environments except production
#     pass
# else:
#     pass
#     # do nothing

# # file path prefix
# stack_prefix = f"https://{CODE_ENVIRONMENT}-cloudformation-files-renzen.s3.us-west-1.amazonaws.com/cloudformation"


# # stacks created or updated in this script
# stacks_order: List[str] = [
#     "cloudformation_deploy.yml",
#     "roles.yml",
#     "network.yml",
#     "resources.yml",
#     "bot.yml",
# ]

# # convert file names to stack compliant names
# stacks_name_compliant = [
#     file.replace("_", "").replace(".yml", "") for file in stacks_order
# ]

# stacks_zipped = zip(stacks_order, stacks_name_compliant)

# print(f"Creating or Updating: {stacks_zipped}")

# # get cloudformation client to get current stacks
# cloudformation_client = boto3.client("cloudformation")

# for stack_name, stack_name_compliant in stacks_zipped:

#     try:
#         print(f"Starting to process: {stack_name}")
#         stack_summary = cloudformation_client.describe_stacks(
#             StackName=stack_name_compliant
#         )
#         print(f"{stack_summary=}")
#     except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as e:
#         # stack does NOT, so attempt to create
#         print(f"Stack does not exist. Attempting to create {stack_name_compliant} {e}")
#         create_response = cloudformation_client.create_stack(
#             StackName=stack_name_compliant,
#             Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
#             TemplateURL=f"{stack_prefix}/{stack_name}",
#         )
#         cloudformation_client.get_waiter("stack_create_complete").wait(
#             StackName=stack_name_compliant
#         )
#         print(f"Created: {stack_name_compliant}")

#     else:
#         # stack exists, so attempt to update
#         try:
#             print(f"Stack exists. Attempting to update {stack_name_compliant}...")
#             update_response = cloudformation_client.update_stack(
#                 StackName=stack_name_compliant,
#                 Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
#                 TemplateURL=f"{stack_prefix}/{stack_name}",
#             )
#             cloudformation_client.get_waiter("stack_update_complete").wait(
#                 StackName=stack_name_compliant
#             )
#             print(f"Updated: {stack_name_compliant}")
#         except (
#             botocore.exceptions.ValidationError,
#             botocore.exceptions.ClientError,
#         ) as e:
#             # update failed due to no updates
#             print(f"No updates for: {stack_name_compliant}")
#             print(f"{e}")
#     finally:
#         print(f"Done processing: {stack_name}")
