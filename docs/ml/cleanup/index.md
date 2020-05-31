# Cleanup Lab Resources

By using the Aurora machine learning labs, you have created additional AWS resources. We recommend you run the commands below to remove these resources once you have completed these labs, to ensure you do not incur any unwanted charges for using these services.  

If you are not already connected to the Session Manager workstation, please connect [following these instructions](/prereqs/connect/). Once connected, run the following commands:

```shell
aws sagemaker delete-endpoint --endpoint-name auroraml-churn-endpoint

aws sagemaker delete-endpoint-config --endpoint-config-name auroraml-churn-endpoint

aws sagemaker delete-model --model-name $(aws sagemaker list-models --output text --query 'Models[*].[ModelName]' | grep sagemaker-scikit-learn)

aws rds remove-role-from-db-cluster --db-cluster-identifier auroralab-mysql-cluster \
--role-arn $(aws iam list-roles --query 'Roles[?RoleName==`auroralab-comprehend-access`].Arn' --output text)

sleep 2m

aws rds remove-role-from-db-cluster --db-cluster-identifier auroralab-mysql-cluster \
--role-arn $(aws iam list-roles --query 'Roles[?RoleName==`auroralab-sagemaker-access`].Arn' --output text)

sleep 2m

aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name $DBCLUSTERPG \
--parameters "ParameterName=aws_default_comprehend_role,ParameterValue='',ApplyMethod=pending-reboot"

aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name $DBCLUSTERPG \
--parameters "ParameterName=aws_default_sagemaker_role,ParameterValue='',ApplyMethod=pending-reboot"

aws rds failover-db-cluster --db-cluster-identifier auroralab-mysql-cluster

aws iam delete-role-policy --role-name auroralab-comprehend-access --policy-name inline-policy

aws iam delete-role-policy --role-name auroralab-sagemaker-access --policy-name inline-policy

aws iam delete-role --role-name auroralab-comprehend-access

aws iam delete-role --role-name auroralab-sagemaker-access
```
