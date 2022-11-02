DISCORD_TOKEN="MTAxMzk4NjQ1MDY5MTMzMDA1OA.GV3Qi8.Yal7EreHMiWICrvd0Czd0_ICNbs-rjAxCEnUsA"

setup:
	chmod a+x bash_setup.sh
	./bash_setup.sh

off:
	aws cloudformation delete-stack --stack-name bot-stack; \


perm:
	aws cloudformation create-stack \
		--stack-name perm-stack \
		--template-body file://cloudformation/perm_resources.yml \
		--parameters \
		ParameterKey="DiscordTokenParameter",ParameterValue="$(DISCORD_TOKEN)" \
		ParameterKey="GitHubRepoName",ParameterValue="renadvent/eklie" \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \
		echo "Activate Github Connection here: console.aws.amazon.com/codesuite/settings/connections"

on:
	aws cloudformation create-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/stack.yml \
		--capabilities CAPABILITY_NAMED_IAM; \

update:
	aws cloudformation update-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/stack.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM


update-setup:
	aws cloudformation update-stack \
		--stack-name perm-stack \
		--template-body file://cloudformation/perm_resources.yml \
		--parameters \
		ParameterKey="DiscordTokenParameter",ParameterValue="$(DISCORD_TOKEN)" \
		ParameterKey="GitHubRepoName",ParameterValue="renadvent/eklie" \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \

pipeline:
	aws codepipeline start-pipeline-execution --name BotCodePipeline