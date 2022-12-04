"""Deregister task defintions so old ones aren't used accidently by service."""

import boto3

client = boto3.client("ecs")

families = ["bot-task", "site-task"]

print("Getting task definitions to deregister.")

for family in families:
    response = client.list_task_definitions(familyPrefix=family)

    task_definitions = response["taskDefinitionArns"]

    while "NextToken" in response:

        response = client.list_task_definitions(
            familyPrefix=family, nextToken=response["NextToken"]
        )
        task_definitions.extend(response["taskDefinitionArns"])

    print(task_definitions)

    for task_definition in task_definitions:

        print(f"Deregistering {task_definition}")

        deregister_response = client.deregister_task_definition(
            taskDefinition=task_definition
        )

print("done deregistering")
