# pylint:disable=invalid-name, line-too-long, broad-except, f-string-without-interpolation
"""Uploads cloudformation files to s3, calls stacks"""
from typing import List

import boto3
import botocore.exceptions

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
print(f"Creating or Updating: {stacks_name_compliant}")

# get cloudformation client to get current stacks
cloudformation_client = boto3.client("cloudformation")

for stack_name in stacks_name_compliant:

    try:
        stack_summary = cloudformation_client.describe_stacks(StackName=stack_name)
        print(f"{stack_summary=}")
        # stack exists, so attempt to update
        print(f"Stack exists. Attempting to update {stack_name}...")
        update_response = cloudformation_client.update_stack(
            StackName=stack_name,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
        )
        role_waiter = cloudformation_client.get_waiter("stack_update_complete").wait(
            StackName=stack_name
        )
        print(f"Updated: {stack_name}")
    except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as e:
        # stack does NOT, so attempt to create
        print(f"Stack does not exist. Attempting to create {stack_name}")
        create_response = cloudformation_client.create_stack(
            StackName=stack_name,
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
        )
        role_waiter = cloudformation_client.get_waiter("stack_create_complete").wait(
            StackName=stack_name
        )
        print(f"Created: {stack_name}")
