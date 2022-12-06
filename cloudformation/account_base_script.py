# pylint:disable=invalid-name, line-too-long, broad-except, f-string-without-interpolation
"""Uploads cloudformation files to s3, calls stacks"""
import os
from typing import List

import boto3
import s3fs  # type: ignore

s3_file = s3fs.S3FileSystem()
local_path = "cloudformation"
s3_path = "s3://cloudformation-files-renzen/cloudformation/"
s3_file.rm(s3_path, recursive=True, maxdepth=10)
s3_file.put(local_path, s3_path, recursive=True)

# get cloudformation client
cloudformation_client = boto3.client("cloudformation")

# apply stacks

directories: List[str] = os.listdir("cloudformation/stacks/")

# run the each stack directorys `root.yml`
response = cloudformation_client.describe_stacks()

# get all stacks
stack_summaries = response["Stacks"]
print(stack_summaries)
while "NextToken" in response:
    response = cloudformation_client.describe_stacks(NextToken=response["NextToken"])
    stack_summaries.extend(response["Stacks"])

role_url = "https://cloudformation-files-renzen.s3.us-west-1.amazonaws.com/cloudformation/roles.yml"
# check for role stack first
for stack in stack_summaries:
    if stack["StackName"] == "roles":
        print("Updating 'role' stack...")

        try:
            create_response = cloudformation_client.update_stack(
                StackName="roles",
                TemplateURL=role_url,
                Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
            )
            role_waiter = cloudformation_client.get_waiter("stack_update_complete")
            if role_waiter:
                role_waiter.wait(StackName="roles")
        except Exception as e:
            print(f"COULD NOT UPDATE: {e}")
        break
else:
    print("Creating 'role' stack...")
    create_response = cloudformation_client.create_stack(
        StackName="roles",
        TemplateURL=role_url,
        Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
    )

    role_waiter = cloudformation_client.get_waiter("stack_create_complete")
    if role_waiter:
        role_waiter.wait(StackName="roles")


# wait until stack is updated or created


# loop over directories (which correspond with stack names)
# and create/update as necessary

stack_prefix = "https://cloudformation-files-renzen.s3.us-west-1.amazonaws.com/cloudformation/stacks"


for directory in directories:

    dir_stack_compliant_name = directory.replace("_", "").replace(".yml", "")
    print(f"{directory=}")
    print(f"{dir_stack_compliant_name=}")

    for stack in stack_summaries:

        print(f"{stack=}")
        stackName = stack["StackName"]
        stackstatus = stack["StackStatus"]

        if stackName == dir_stack_compliant_name:
            print(f"{stackName} exists with matching directory name")

            if stackstatus in ["CREATE_COMPLETE", "UPDATE_COMPLETE"]:
                print(f"Stack {stackName} can be updated...")

                try:
                    print(f"Attempting to update {stackName}...")
                    update_response = cloudformation_client.update_stack(
                        StackName=dir_stack_compliant_name,
                        TemplateURL=f"{stack_prefix}/{directory}/root.yml",
                        Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
                    )
                    # not async rn
                    cloudformation_client.get_waiter("stack_update_complete").wait(
                        StackName=stackName
                    )
                    print(f"Stack {stackName} was updated...")
                    print(f"Moving on to next directory")
                    break

                except Exception as e:
                    print(f"Stack {stackName} was NOT updated: {e}")
                    print(f"Moving on to next directory")
                    break

            elif stackstatus in ["ROLLBACK_COMPLETE"]:

                print(
                    f'stack {stack["StackName"]} in ROLLBACK_COMPLETE state. Deleting...'
                )

                cloudformation_client.delete_stack(StackName=dir_stack_compliant_name)
                role_waiter = cloudformation_client.get_waiter("stack_delete_complete")
                role_waiter.wait(StackName=dir_stack_compliant_name)

                print(f'Creating after deleting {stack["StackName"]}...')
                create_response = cloudformation_client.create_stack(
                    StackName=dir_stack_compliant_name,
                    TemplateURL=f"{stack_prefix}/{directory}/root.yml",
                    Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
                )
                cloudformation_client.get_waiter("stack_create_complete").wait(
                    StackName=dir_stack_compliant_name
                )
                print(f"Moving on to next directory")
                break

    # directory has not corresponding stack created, so create
    else:
        print(f"Creating {dir_stack_compliant_name}...")
        create_response = cloudformation_client.create_stack(
            StackName=dir_stack_compliant_name,
            TemplateURL=f"{stack_prefix}/{directory}/root.yml",
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
        )
        cloudformation_client.get_waiter("stack_create_complete").wait(
            StackName=dir_stack_compliant_name
        )
