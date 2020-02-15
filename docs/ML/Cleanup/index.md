Connect to the session manager using the instructions [here](/prereqs/connect/) and execute following commands to cleanup Sagemaker resoucres and roles.


``` shell

aws sagemaker delete-endpoint --endpoint-name AuroraML-churn-endpoint

aws sagemaker delete-endpoint-config --endpoint-config-name AuroraML-churn-endpoint

aws sagemaker delete-model --model-name $(aws sagemaker list-models --output text --query 'Models[*].[ModelName]' | grep sagemaker-scikit-learn)

aws s3 rm s3://$(aws s3api list-buckets --output text  --query 'Buckets[?Name].{Name:Name}' |grep labstack-auroradata*) --recursive

aws iam detach-role-policy --role-name ComprehendAuroraAccessRole --policy-arn $(aws iam list-policies --query 'Policies[?PolicyName==`ComprehendAuroraPolicy`].Arn' --output text)

aws iam detach-role-policy --role-name SageMakerAuroraAccessRole --policy-arn $(aws iam list-policies --query 'Policies[?PolicyName==`SagemakerAuroraPolicy`].Arn' --output text)

aws iam delete-role --role-name ComprehendAuroraAccessRole

aws iam delete-role --role-name SagemakerAuroraAccessRole

aws iam delete-policy --policy-arn $(aws iam list-policies --query 'Policies[?PolicyName==`ComprehendAuroraPolicy`].Arn' --output text)

aws iam delete-policy --policy-arn $(aws iam list-policies --query 'Policies[?PolicyName==`SagemakerAuroraPolicy`].Arn' --output text)




```