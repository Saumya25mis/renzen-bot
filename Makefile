init:
	chmod a+x scripts/init_setup.sh
	./scripts/init_setup.sh

setup-bot:
	chmod a+x scripts/configure_setup.sh
	./scripts/configure_setup.sh

wipe-setup:
	aws cloudformation delete-stack --stack-name secret-stack

bot-on:
	aws cloudformation create-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/bot_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM; \

bot-off:
	aws cloudformation delete-stack --stack-name bot-stack; \

start-pipeline:
	aws codepipeline start-pipeline-execution --name BotCodePipeline