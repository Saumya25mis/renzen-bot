"""Uploads cloudformation files to s3, calls stacks"""
from typing import List

import boto3
import s3fs  # type: ignore

# from mypy_boto3_cloudformation.client import CloudFormationClient
# from mypy_boto3_s3.client import S3Client

s3_file_system: s3fs.S3FileSystem = s3fs.S3FileSystem()
# upload files to s3
s3_file_system.put(
    rpath="cloudformation/",
    lpath="s3://cloudformation-files-renzen/cloudformation/",
    recursive=True,
)

# get cloudformation client
cloudformation_client = boto3.client("cloudformation")

# apply stacks
directories: List[str] = s3_file_system.listdir("cloudformation/stacks")

# run the each stack directorys `root.yml`
response = cloudformation_client.list_stacks()

# get all stacks
stack_summaries = response["StackSummaries"]
while "NextToken" in response:
    response = cloudformation_client.list_stacks(NextToken=response["NextToken"])
    stack_summaries.extend(response["StackSummaries"])

# check for role stack first
for stack in stack_summaries:
    if stack["StackName"] == "roles.yml":
        create_response = cloudformation_client.update_stack(
            StackName="roles.yml",
            TemplateURL="s3://cloudformation-files-renzen/cloudformation/roles.yml",
        )
        role_waiter = cloudformation_client.get_waiter("stack_update_complete")
        break
else:
    create_response = cloudformation_client.create_stack(
        StackName="roles.yml",
        TemplateURL="s3://cloudformation-files-renzen//cloudformation/roles.yml",
    )

    role_waiter = cloudformation_client.get_waiter("stack_create_complete")


# wait until stack is updated or created
role_waiter.wait(StackName="roles.yml")

# loop over directories (which correspond with stack names)
# and create/update as necessary
for directory in directories:

    for stack in stack_summaries:

        # deal with stacks that exist
        compliant = directory.replace("_", "")
        if stack["StackName"] == compliant:

            status = stack["StackStatus"]
            if status == "CREATE_COMPLETE":
                update_response = cloudformation_client.update_stack(
                    StackName=compliant,
                    TemplateURL=f"cloudformation-s3-bucket/cloudformation/{directory}/root.yml",
                )
                # not async rn
                cloudformation_client.get_waiter("stack_update_complete").wait(
                    StackName=stack["StackName"]
                )
            else:
                # FAIL DEPLOY
                pass

        # deal with stacks that DONT exist
        else:
            create_response = cloudformation_client.create_stack(
                StackName=directory,
                TemplateURL=f"cloudformation-s3-bucket/cloudformation/{directory}/root.yml",
            )
            cloudformation_client.get_waiter("stack_create_complete").wait(
                StackName=stack["StackName"]
            )
