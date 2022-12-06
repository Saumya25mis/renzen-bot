# pylint:disable=invalid-name, line-too-long, broad-except, f-string-without-interpolation
"""Uploads cloudformation files to s3, calls stacks"""
from typing import List

import boto3
import botocore.exceptions

# file path prefix
stack_prefix = (
    "https://cloudformation-files-renzen.s3.us-west-1.amazonaws.com/cloudformation"
)

# stacks created or updated in this script
stacks_order: List[str] = [
    "roles.yml",
    "init_stack.yml",
    "bot.yml",
]

# convert file names to stack compliant names
stacks_name_compliant = [
    file.replace("_", "").replace(".yml", "") for file in stacks_order
]

stacks_zipped = zip(stacks_order, stacks_name_compliant)

print(f"Creating or Updating: {stacks_zipped}")

# get cloudformation client to get current stacks
cloudformation_client = boto3.client("cloudformation")

for stack_name, stack_name_compliant in stacks_zipped:

    try:
        stack_summary = cloudformation_client.describe_stacks(
            StackName=stack_name_compliant
        )
        print(f"{stack_summary=}")
        # stack exists, so attempt to update
        print(f"Stack exists. Attempting to update {stack_name_compliant}...")
        update_response = cloudformation_client.update_stack(
            StackName=stack_name_compliant,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            TemplateURL=f"{stack_prefix}/{stack_name}",
        )
        cloudformation_client.get_waiter("stack_update_complete").wait(
            StackName=stack_name_compliant
        )
        print(f"Updated: {stack_name_compliant}")
    except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as e:
        # stack does NOT, so attempt to create
        print(f"Stack does not exist. Attempting to create {stack_name_compliant}")
        create_response = cloudformation_client.create_stack(
            StackName=stack_name_compliant,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            TemplateURL=f"{stack_prefix}/{stack_name}",
        )
        cloudformation_client.get_waiter("stack_create_complete").wait(
            StackName=stack_name_compliant
        )
        print(f"Created: {stack_name_compliant}")
