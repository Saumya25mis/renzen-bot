# aws cloudformation wait stack-create-complete --stack-name myStackName


init-aws:
	chmod a+x scripts/init_setup.sh
	./scripts/init_setup.sh

configure-bot:
	chmod a+x scripts/configure_setup.sh
	./scripts/configure_setup.sh



start-bot:
	aws cloudformation create-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/bot_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM; \

update-bot:
	aws cloudformation update-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/bot_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM; \


update-domain:
	aws cloudformation update-stack \
		--stack-name domain-stack \
		--template-body file://cloudformation/domain_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM; \

domain:
	aws cloudformation create-stack \
		--stack-name domain-stack \
		--template-body file://cloudformation/domain_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM; \

stop-bot:
	aws cloudformation delete-stack --stack-name bot-stack; \

wipe-configure:
	aws cloudformation delete-stack --stack-name configure-stack



start-pipeline:
	aws codepipeline start-pipeline-execution --name BotCodePipeline