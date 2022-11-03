setup-bot:
	chmod a+x bash_setup.sh
	./bash_setup.sh


bot-on:
	aws cloudformation create-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/stack.yml \
		--capabilities CAPABILITY_NAMED_IAM; \


bot-off:
	aws cloudformation delete-stack --stack-name bot-stack; \


update-bot-stack:
	aws cloudformation update-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/stack.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM


start-pipeline:
	aws codepipeline start-pipeline-execution --name BotCodePipeline