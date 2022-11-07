#!/bin/bash

# configure AWS
echo "Enter AWS credentials to setup resources in AWS"
aws configure

# get discord token
read -p "Provide Discord Bot Token (https://discord.com/developers/applications): " DISCORD_TOKEN
read -p "AWS_ACCOUNT_ID: " AWS_ACCOUNT_ID
read -p "Github Repository name: " GitHubRepoName
read -p "Bot name: " BotName
read -p "Branch Name: " BranchName

# create stack bot will use to run
aws cloudformation create-stack \
    --stack-name configure-stack \
    --template-body file://cloudformation/configure_stack.yml \
    --parameters \
    ParameterKey="DiscordTokenParameter",ParameterValue=$DISCORD_TOKEN \
    ParameterKey="GitHubRepoName",ParameterValue=$GitHubRepoName \
    ParameterKey="AWSACCOUNTID",ParameterValue=$AWS_ACCOUNT_ID \
    --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \
    echo "Activate Github Connection here: console.aws.amazon.com/codesuite/settings/connections"

echo "Change git connection to Available. Bot will not be able to deploy until this is done."
echo "Add bot to guild!"