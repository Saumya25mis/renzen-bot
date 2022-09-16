DISCORD_TOKEN="MTAxMzk4NjQ1MDY5MTMzMDA1OA.GV3Qi8.Yal7EreHMiWICrvd0Czd0_ICNbs-rjAxCEnUsA"

setup:
	chmod a+x bash_setup.sh
	./bash_setup.sh

delete:
	aws cloudformation delete-stack --stack-name bot-stack; \

bot:
	aws cloudformation create-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/stack.yml \
		--parameters \
		ParameterKey="DiscordTokenParameter",ParameterValue="$(DISCORD_TOKEN)" \
		ParameterKey="GitHubRepoName",ParameterValue="renadvent/eklie" \
		--capabilities CAPABILITY_NAMED_IAM; \
		echo "Activate Github Connection here: console.aws.amazon.com/codesuite/settings/connections"

update:
	aws cloudformation update-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/stack.yml \
		--parameters \
		ParameterKey="DiscordTokenParameter",ParameterValue="$(DISCORD_TOKEN)" \
		ParameterKey="GitHubRepoName",ParameterValue="renadvent/eklie" \
		--capabilities CAPABILITY_NAMED_IAM

pipeline:
	aws codepipeline start-pipeline-execution --name BotCodePipeline