# pylint:disable=invalid-name, line-too-long, broad-except
"""Uploads cloudformation files to s3, calls stacks"""
import os
from typing import List

import boto3
import s3fs  # type: ignore

s3_file = s3fs.S3FileSystem()
local_path = "cloudformation/"
s3_path = "s3://cloudformation-files-renzen/cloudformation/"
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

    print(directory)

    for stack in stack_summaries:

        # deal with stacks that exist
        compliant = directory.replace("_", "").replace(".yml", "")
        if stack["StackName"] == compliant:
            print(stack)
            status = stack["StackStatus"]
            if status in ["CREATE_COMPLETE", "ROLLBACK_COMPLETE", "UPDATE_COMPLETE"]:
                print(f'Updating {stack["StackName"]}...')

                try:
                    update_response = cloudformation_client.update_stack(
                        StackName=compliant,
                        TemplateURL=f"{stack_prefix}/{directory}/root.yml",
                        Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
                    )
                    # not async rn
                    cloudformation_client.get_waiter("stack_update_complete").wait(
                        StackName=stack["StackName"]
                    )
                    break

                except Exception as e:
                    print(f"COULD NOT UPDATE: {e}")
                    break
            # else:
            #     # FAIL DEPLOY
            #     print(
            #         f'Stack {stack["StackName"]} could not be updated due to {stack["StackStatus"]} !'
            #     )
            #     break

    # directory has not corresponding stack created, so create
    else:
        print(f'Creating {stack["StackName"]}...')
        create_response = cloudformation_client.create_stack(
            StackName=compliant,
            TemplateURL=f"{stack_prefix}/{directory}/root.yml",
            Capabilities=["CAPABILITY_IAM", "CAPABILITY_NAMED_IAM"],
        )
        cloudformation_client.get_waiter("stack_create_complete").wait(
            StackName=stack["StackName"]
        )
