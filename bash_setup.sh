#!/bin/bash

# configure AWS
# echo "Enter AWS credentials to setup resources in AWS"
aws configure

# get discord token
read -p "Enter Discord Bot Token (https://discord.com/developers/applications): " DISCORD_TOKEN

# DISCORD_TOKEN="MTAxMzk4NjQ1MDY5MTMzMDA1OA.GV3Qi8.Yal7EreHMiWICrvd0Czd0_ICNbs-rjAxCEnUsA"

# create stack bot will use to run
aws cloudformation create-stack \
    --stack-name bot-stack \
    --template-body file://cloudformation/stack.yml \
    --parameters \
    ParameterKey="DiscordTokenParameter",ParameterValue="$DISCORD_TOKEN" \
    ParameterKey="GitHubRepoName",ParameterValue="eklie" \
    --capabilities CAPABILITY_NAMED_IAM

echo "Change git connection to Available. Bot will not deploy until this is done."
echo "Add bot to guild!"