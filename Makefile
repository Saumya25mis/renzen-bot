#!/bin/bash

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

AWS_ACCOUNT_ID = $(aws sts get-caller-identity --query "Account" --output text)

run-local:
	docker compose up --build

deploy-prod:
	aws cloudformation create-stack \
		--stack-name productiondeploy8 \
		--template-body file://cloudformation/bot_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM \
		--parameters \
		ParameterKey="DiscordToken",ParameterValue=${PRODUCTION_DISCORD_TOKEN} \
		ParameterKey="GitHubRepoName",ParameterValue=${PRODUCTION_GITHUB_REPO} \
		ParameterKey="GitHubBranchName",ParameterValue=${PRODUCTION_GITHUB_BRANCH} \
		ParameterKey="CodeEnvironment",ParameterValue="production8" \
		ParameterKey="HostedZoneId",ParameterValue=${HOSTED_ZONE_ID} \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \

deploy-staging:
	aws cloudformation create-stack \
		--stack-name stagingdeploy \
		--template-body file://cloudformation/bot_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM \
		--parameters \
		ParameterKey="DiscordToken",ParameterValue=${STAGING_DISCORD_TOKEN} \
		ParameterKey="GitHubRepoName",ParameterValue=${STAGING_DISCORD_REPO} \
		ParameterKey="GitHubBranchName",ParameterValue=${STAGING_DISCORD_BRANCH} \
		ParameterKey="CodeEnvironment",ParameterValue="staging" \
		ParameterKey="HostedZoneId",ParameterValue=${HOSTED_ZONE_ID} \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \

update-prod:
	aws cloudformation create-stack \
		--stack-name productiondeploy \
		--template-body file://cloudformation/bot_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM \
		--parameters \
		ParameterKey="DiscordToken",ParameterValue=${PRODUCTION_DISCORD_TOKEN} \
		ParameterKey="GitHubRepoName",ParameterValue=${PRODUCTION_GITHUB_REPO} \
		ParameterKey="GitHubBranchName",ParameterValue=${PRODUCTION_GITHUB_BRANCH} \
		ParameterKey="CodeEnvironment",ParameterValue="production" \
		ParameterKey="HostedZoneId",ParameterValue=${HOSTED_ZONE_ID} \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \

update-staging:
	aws cloudformation create-stack \
		--stack-name stagingdeploy \
		--template-body file://cloudformation/bot_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM \
		--parameters \
		ParameterKey="DiscordToken",ParameterValue=${STAGING_DISCORD_TOKEN} \
		ParameterKey="GitHubRepoName",ParameterValue=${STAGING_DISCORD_REPO} \
		ParameterKey="GitHubBranchName",ParameterValue=${STAGING_DISCORD_BRANCH} \
		ParameterKey="CodeEnvironment",ParameterValue="staging" \
		ParameterKey="HostedZoneId",ParameterValue=${HOSTED_ZONE_ID} \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \

sync-cloudformation:
	aws s3 sync cloudformation "s3://cloudformation-files-renzen/cloudformation/"

github-connect:
	aws cloudformation update-stack \
		--stack-name githubconnect \
		--template-body file://cloudformation/github_connect.yml \
		--capabilities CAPABILITY_NAMED_IAM; \

bot-logs:
	aws logs tail bot-task --follow

site-logs:
	aws logs tail bot-site --follow
