Connect to the session manager using the instructions [here](/prereqs/connect/) and execute following commands to cleanup Sagemaker resources and roles.


``` shell

aws sagemaker delete-endpoint --endpoint-name AuroraML-churn-endpoint

aws sagemaker delete-endpoint-config --endpoint-config-name AuroraML-churn-endpoint

aws sagemaker delete-model --model-name $(aws sagemaker list-models --output text --query 'Models[*].[ModelName]' | grep sagemaker-scikit-learn)

aws s3 rm s3://$DATABUCKET --recursive

aws iam detach-role-policy --role-name $STACKNAME-ComprehendAuroraAccessRole-$STACKREGION --policy-arn $(aws iam list-policies --query "Policies[?PolicyName=='$STACKNAME-ComprehendAuroraPolicy-$STACKREGION'].Arn" --output text)

aws iam detach-role-policy --role-name $STACKNAME-SageMakerAuroraAccessRole-$STACKREGION --policy-arn $(aws iam list-policies --query "Policies[?PolicyName=='$STACKNAME-SagemakerAuroraPolicy-$STACKREGION'].Arn" --output text)

aws iam delete-role --role-name $STACKNAME-ComprehendAuroraAccessRole-$STACKREGION

aws iam delete-role --role-name $STACKNAME-SagemakerAuroraAccessRole-$STACKREGION

aws iam delete-policy --policy-arn $(aws iam list-policies --query "Policies[?PolicyName=='$STACKNAME-ComprehendAuroraPolicy-$STACKREGION'].Arn" --output text)

aws iam delete-policy --policy-arn $(aws iam list-policies --query "Policies[?PolicyName=='$STACKNAME-SagemakerAuroraPolicy-$STACKREGION'].Arn" --output text)

```