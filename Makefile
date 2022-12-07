create-deploy-process:
	aws cloudformation update-stack \
		--stack-name cloudformationdeploy \
		--template-body file://cloudformation/cloudformation_deploy.yml \
		--capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM; \

sync-cloudformation:
	aws s3 sync cloudformation "s3://cloudformation-files-renzen/cloudformation/"

github-connect:
	aws cloudformation update-stack \
		--stack-name githubconnect \
		--template-body file://cloudformation/github_connect.yml \
		--capabilities CAPABILITY_NAMED_IAM; \

configure-bot:
	chmod a+x scripts/configure_setup.sh
	./scripts/configure_setup.sh

bot-logs:
	aws logs tail bot-task --follow

site-logs:
	aws logs tail bot-site --follow

codebuild-logs:
	aws logs tail "/aws/codebuild/BotCodeBuildProject" --follow
