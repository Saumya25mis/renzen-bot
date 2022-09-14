#!/bin/bash

REPOSITORY_NAME = "bot-images"

# get crdentials
read - "Enter Discord Bot Token: " DISCORD_TOKEN
read - "Enter AWS_ACCESS_KEY_ID: " AWS_ACCESS_KEY_ID
read - "Enter AWS_SECRET_ACCESS_KEY: " AWS_SECRET_ACCESS_KEY

# export AWS secrets for aws cli
export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

# create bot token secret in AWS
aws secretsmanager create-secret \
    --name DISCORD_TOKEN \
    --description "Discord token for bot." \
    --secret-string "{\"DISCORD_TOKEN\": "$DISCORD_TOKEN"}"

aws cloudformation create-stack \
    --stack-name bot-cluster-def \
    --template-body file://cloudformation/stack.yml

# pipeline buildspec
aws codepipeline create-pipeline \
    --cli-input-json file://cloudformation/pipeline.json