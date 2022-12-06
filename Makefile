github-connect:
	aws cloudformation create-stack \
		--stack-name githubconnect \
		--template-body file://cloudformation/stacks/bot_stack/manual/github_connect.yml \
		--capabilities CAPABILITY_NAMED_IAM; \

create-base:
	aws cloudformation update-stack \
		--stack-name accountbasestack \
		--template-body file://cloudformation/account_base_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \

create-bot-root:
	aws cloudformation create-stack \
		--stack-name botstack \
		--template-body file://cloudformation/stacks/bot_stack/root.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \

update-base:
	aws cloudformation update-stack \
		--stack-name accountbasestack \
		--template-body file://cloudformation/account_base_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \

init-aws:
	chmod a+x scripts/init_setup.sh
	./scripts/init_setup.sh

configure-bot:
	chmod a+x scripts/configure_setup.sh
	./scripts/configure_setup.sh

update-init:
	aws cloudformation update-stack \
		--stack-name init-stack \
		--template-body file://cloudformation/init_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM;

aws cloudformation delete-stack \
	--stack-name init-stack \
	--template-body file://cloudformation/init_stack.yml \
	--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM;

start-bot:
	aws cloudformation create-stack \
		--stack-name bot-stack \
		--template-body file://cloudformation/bot_stack.yml \
		--capabilities CAPABILITY_NAMED_IAM; \

start-pipeline:
	aws cloudformation create-stack \
		--stack-name pipeline-stack \
		--template-body file://cloudformation/pipeline_stack.yml \
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

bot-logs:
	aws logs tail bot-task --follow

site-logs:
	aws logs tail bot-site --follow

codebuild-logs:
	aws logs tail "/aws/codebuild/BotCodeBuildProject" --follow
