# configure AWS
echo "Enter AWS credentials to setup resources in AWS"
aws configure

# create stack bot will use to run
aws cloudformation create-stack \
    --stack-name init-stack \
    --template-body file://cloudformation/init_stack.yml \
    --capabilities CAPABILITY_NAMED_IAM CAPABILITY_IAM;

echo "Activate Github Connection here: console.aws.amazon.com/codesuite/settings/connections"