#!/bin/bash

# configure AWS
# echo "Enter AWS credentials to setup resources in AWS"
aws configure

# get discord token
read -p "Enter Discord Bot Token (https://discord.com/developers/applications): " DISCORD_TOKEN
# read -p "AWS_ACCOUNT_ID: " AWS_ACCOUNT_ID
read -p "Github Repository name: " GitHubRepoName
read -p "Bot name: " BotName

# DISCORD_TOKEN="MTAxMzk4NjQ1MDY5MTMzMDA1OA.GV3Qi8.Yal7EreHMiWICrvd0Czd0_ICNbs-rjAxCEnUsA"
# AWS_ACCOUNT_ID: "103443233719"

# aws ec2 describe-security-groups --group-names default --query SecurityGroups[0].VpcId
# aws ec2 describe-subnets --query Subnets[?DefaultForAz].SubnetArn
# SUBNETS=$(aws ec2 describe-subnets --query Subnets[?DefaultForAz].SubnetArn)
# SECURITY_GROUP =$(aws ec2 describe-security-groups --group-names default --query SecurityGroups[0].VpcId)



#     ParameterKey="SUBNETS",ParameterValue="$SUBNETS" \
#     ParameterKey="SECURITY_GROUP",ParameterValue="$SECURITY_GROUP"

# create stack bot will use to run
aws cloudformation create-stack \
    --stack-name perm-stack \
    --template-body file://cloudformation/perm_resources.yml \
    --parameters \
    ParameterKey="DiscordTokenParameter",ParameterValue="$DISCORD_TOKEN" \
    ParameterKey="GitHubRepoName",ParameterValue="eklie" \
    # ParameterKey="AWS_ACCOUNT_ID", ParameterValue="$AWS_ACCOUNT_ID" \
    --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM

echo "Change git connection to Available. Bot will not be able to deploy until this is done."
echo "Afterwards run `make pipeline` to manually run it if it has failed"
echo "Add bot to guild!"