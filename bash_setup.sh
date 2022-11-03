#!/bin/bash

# configure AWS
echo "Enter AWS credentials to setup resources in AWS"
aws configure

# get discord token
read -p "Provide Discord Bot Token (https://discord.com/developers/applications): " DISCORD_TOKEN
read -p "AWS_ACCOUNT_ID: " AWS_ACCOUNT_ID
read -p "Github Repository name: " GitHubRepoName
read -p "Bot name: " BotName

# create stack bot will use to run
aws cloudformation create-stack \
    --stack-name perm-stack \
    --template-body file://cloudformation/perm_resources.yml \
    --parameters \
    ParameterKey="DiscordTokenParameter",ParameterValue="$(DISCORD_TOKEN)" \
    ParameterKey="GitHubRepoName",ParameterValue="renadvent/eklie" \
    ParameterKey="AWSACCOUNTID",ParameterValue="103443233719" \
    --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \
    echo "Activate Github Connection here: console.aws.amazon.com/codesuite/settings/connections"

echo "Change git connection to Available. Bot will not be able to deploy until this is done."
echo "Afterwards run `make pipeline` to manually run it if it has failed"
echo "Add bot to guild!"