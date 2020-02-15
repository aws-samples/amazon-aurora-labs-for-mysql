This lab will walk you through the process of provisioning the inrastructure needed to create and call Comprehend function from Amazon Aurora.

## Pre-requisits
Before running the lab make sure you have met the followin pre-requisits.

* [Deploy Environment](/prereqs/environment/) (using the `lab-with-cluster.yml` template)
* [Connect to the Session Manager Workstation](/prereqs/connect/)
* [Comprehend on Aurora](/ML/Comprehend/)

## This lab contains following tasks:

1. Create IAM role required by Aurora to Talk to Sagemaker.
2. Create and attach policy to the role.
3. Associate the IAM role with the Aurora cluster.
4. Add the Sagemaker role to the db cluster parameter group.
5. Create the SageMaker function.
6. Exececute the function and observe predictions.  


## 1. Create IAM role required by Aurora to Talk to Sagemaker

If you are not already connected to the Session Manager workstation command line from previous labs, please connect [following these instructions](/prereqs/connect/). Once connected, run the commands below.

``` shell
aws iam create-role --role-name SagemakerAuroraAccessRole \
--assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"rds.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
```

## 2. Create and attach policy to the role

We will download the policy file, update it with the sagmaker endpoint, and then attach the policy to the role using following commands.

``` shell
curl -O https://raw.githubusercontent.com/aws-samples/amazon-aurora-labs-for-mysql/master/support/SMAuroraPolicy.json

sed -i "s%EndpointArn%$(aws sagemaker describe-endpoint --endpoint-name AuroraML-churn-endpoint --query [EndpointArn] --output text)%" SMAuroraPolicy.json

aws iam create-policy --policy-name SagemakerAuroraPolicy --policy-document file://SMAuroraPolicy.json

aws iam attach-role-policy --role-name SagemakerAuroraAccessRole --policy-arn $(aws iam list-policies --query 'Policies[?PolicyName==`SagemakerAuroraPolicy`].Arn' --output text)

```

## 3. Associate the IAM role with the Aurora cluster

Next step is to associate the IAM role with the cluster. Execute following command to do so, replacing the ==[dbCluster]== placeholder with the name of your DB cluster.

``` shell
aws rds add-role-to-db-cluster --db-cluster-identifier [dbCluster] \
--role-arn $(aws iam list-roles --query 'Roles[?RoleName==`SagemakerAuroraAccessRole`].Arn' --output text)
```		
Run the following command and wait until the output shows as **"available"**, before moving on to the next step.  Replacing the ==[dbCluster]== placeholder with the name of your DB cluster.

``` shell
aws rds describe-db-clusters --db-cluster-identifier [dbCluster] \
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Reader Load](/ML/Comprehend/2-dbcluster-available.png?raw=true)</span>

## 4. Add the Sagemaker role to the db cluster parameter group

``` shell
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name AllowAWSAccessToMLServices \
--parameters "ParameterName=aws_default_sagemaker_role,ParameterValue=$(aws iam list-roles --query 'Roles[?RoleName==`SagemakerAuroraAccessRole`].Arn' --output text),ApplyMethod=immediate"
```

## 5.Create Sagemaker function

execute the commands below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. This will connect you to the Aurora mysql  instance.

``` shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mltest
```

Once connected, execute the following SQL quey to create **will_churn** the function using the ==alias aws_sagemaker_invoke_endpointparameter== parameter and passing the name of the sagemaker endpoint.  

```sql
CREATE FUNCTION `will_churn`(
state varchar(2048), 
acc_length bigint(20),
area_code bigint(20), 
int_plan varchar(2048),
vmail_plan varchar(2048), 
vmail_msg bigint(20),
day_mins double, 
day_calls bigint(20),
eve_mins double, 
eve_calls bigint(20),
night_mins double, 
night_calls bigint(20),
int_mins double, 
int_calls bigint(20),
cust_service_calls bigint(20)) RETURNS varchar(2048) CHARSET latin1
alias aws_sagemaker_invoke_endpoint
endpoint name 'AuroraML-churn-endpoint';
```

## 6. Execute the function and observe predictions  

Now that we have the function created linking back to the sagemaker endpoint, we can pass it values and observer predictions. In the example, we will observe that based on the values passed, prediction is that the this customer **will churn**.

``` sql
select 
will_churn('IN',65,415,'no','no',0,129.1,137,228.5,83,208.8,111,12.7,6,4) as 'Will Churn?';

```
