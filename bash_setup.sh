#!/bin/bash

# get crdentials
# echo "Enter AWS credentials to setup resources in AWS"
# read - "Enter AWS_ACCESS_KEY_ID: " AWS_ACCESS_KEY_ID
# read - "Enter AWS_SECRET_ACCESS_KEY: " AWS_SECRET_ACCESS_KEY
# export AWS secrets for aws cli
# export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
# export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY

# configure github?
# gh auth login


#---------------------------------------------------------------

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

echo "Bot AWS Resources and Codepipeline was successfully setup. Congrats!"
echo "Change git connection to Available"
echo "Add bot to guild!"