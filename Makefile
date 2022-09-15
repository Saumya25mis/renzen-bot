# bash_setup.sh

DISCORD_TOKEN="MTAxMzk4NjQ1MDY5MTMzMDA1OA.GV3Qi8.Yal7EreHMiWICrvd0Czd0_ICNbs-rjAxCEnUsA"

setup:
	chmod a+x bash_setup.sh
	./bash_setup.sh

delete:
	aws cloudformation delete-stack --stack-name bot-stack; \
	aws cloudformation delete-stack --stack-name pipeline-stack

update:
	aws cloudformation update-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/stack.yml \
		--parameters \
		ParameterKey="DiscordTokenParameter",ParameterValue="$(DISCORD_TOKEN)" \
		ParameterKey="GitHubRepoName",ParameterValue="eklie" \
		--capabilities CAPABILITY_NAMED_IAM

bot:
	aws cloudformation delete-stack --stack-name bot-stack; sleep 2 \
	aws cloudformation create-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/stack.yml \
		--parameters \
		ParameterKey="DiscordTokenParameter",ParameterValue="$(DISCORD_TOKEN)" \
		ParameterKey="GitHubRepoName",ParameterValue="renadvent/eklie" \
		--capabilities CAPABILITY_NAMED_IAM

pipeline:
	aws cloudformation delete-stack --stack-name pipeline-stack; sleep 2; \
	aws cloudformation create-stack \
		--stack-name pipeline-stack \
		--template-body file://cloudformation/pipeline.yml \
		--parameters \
		ParameterKey="DiscordTokenParameter",ParameterValue="$(DISCORD_TOKEN)" \
		ParameterKey="GitHubRepoName",ParameterValue="renadvent/eklie" \
		--capabilities CAPABILITY_NAMED_IAM; \
	echo "Activate connection https://us-west-1.console.aws.amazon.com/codesuite/settings/connections"

update-pipeline:
	aws cloudformation update-stack \
		--stack-name pipeline-stack \
		--template-body file://cloudformation/pipeline.yml \
		--parameters \
		ParameterKey="DiscordTokenParameter",ParameterValue="$(DISCORD_TOKEN)" \
		ParameterKey="GitHubRepoName",ParameterValue="renadvent/eklie" \
		--capabilities CAPABILITY_NAMED_IAM; \
	echo "Activate connection https://us-west-1.console.aws.amazon.com/codesuite/settings/connections"
