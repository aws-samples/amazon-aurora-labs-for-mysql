This lab will walk you through the process of provisioning the infrastructure needed to create and call Comprehend function from Amazon Aurora.

## Pre-requisites
Before running the lab make sure you have met the following pre-requisites.

* [Complete the pre-requisites section](/ml/overview/)

## This lab contains following tasks:

1. Create IAM role required by Aurora to Talk to SageMaker.
2. Create and attach policy to the role.
3. Associate the IAM role with the Aurora cluster.
4. Add the SageMaker role to the db cluster parameter group.
5. Apply the new parameter to the database cluster.
6. Create the SageMaker function.
7. Execute the function and observe predictions.  


## 1. Create IAM role required by Aurora to Talk to SageMaker

If you are not already connected to the Session Manager workstation command line from previous labs, please connect [following these instructions](/prereqs/connect/). Once connected, run the commands below.

``` shell
aws iam create-role --role-name $STACKNAME-SagemakerAuroraAccessRole-$STACKREGION \
--assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"rds.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
```

## 2. Create and attach policy to the role

We will download the policy file, update it with the sagmaker endpoint, and then attach the policy to the role using following commands.

``` shell

sed -i "s%EndpointArn%$(aws sagemaker describe-endpoint --endpoint-name AuroraML-churn-endpoint --query [EndpointArn] --output text)%" SMAuroraPolicy.json

aws iam create-policy --policy-name $STACKNAME-SagemakerAuroraPolicy-$STACKREGION --policy-document file://SMAuroraPolicy.json

aws iam attach-role-policy --role-name $STACKNAME-SagemakerAuroraAccessRole-$STACKREGION --policy-arn $(aws iam list-policies --query "Policies[?PolicyName=='$STACKNAME-SagemakerAuroraPolicy-$STACKREGION'].Arn" --output text)

```

## 3. Associate the IAM role with the Aurora cluster

Next step is to associate the IAM role with the cluster.

``` shell
aws rds add-role-to-db-cluster --db-cluster-identifier labstack-cluster \
--role-arn $(aws iam list-roles --query "Roles[?RoleName=='$STACKNAME-SagemakerAuroraAccessRole-$STACKREGION'].Arn" --output text)
```		
Run the following command and wait until the output shows as **"available"**, before moving on to the next step.

``` shell
aws rds describe-db-clusters --db-cluster-identifier labstack-cluster \
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Reader Load](/ml/comprehend/2-dbcluster-available.png?raw=true)</span>

## 4. Add the SageMaker role to the db cluster parameter group

``` shell
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name $DBCLUSTERPG \
--parameters "ParameterName=aws_default_sagemaker_role,ParameterValue=$(aws iam list-roles --query "Roles[?RoleName=='$STACKNAME-SagemakerAuroraAccessRole-$STACKREGION'].Arn" --output text),ApplyMethod=pending-reboot"
```

## 5. Apply the new parameter to the database cluster.
Reboot the db instance so the change can take effect, by executing the commands below.

``` shell
aws rds reboot-db-instance --db-instance-identifier $(aws rds describe-db-clusters --db-cluster-identifier labstack-cluster --query 'DBClusters[*].[DBClusterMembers[?IsClusterWriter==`true`].DBInstanceIdentifier]' --output text)

```
Run the following command and wait until the output shows as **"available"**, before moving on to the next step.

``` shell
aws rds describe-db-instances --db-instance-identifier \
$(aws rds describe-db-clusters --db-cluster-identifier labstack-cluster --query 'DBClusters[*].[DBClusterMembers[?IsClusterWriter==`true`].DBInstanceIdentifier]' --output text) --query 'DBInstances[*].[DBInstanceStatus]' --output text

```

<span class="image">![Reader Load](/ml/sagemaker/3-db-sintance-available.png?raw=true)</span>


## 6.Create SageMaker function

Execute the commands below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. This will connect you to the Aurora MySQL  instance.

``` shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mltest
```

Once connected, execute the following SQL quey to create **will_churn** the function using the ==alias aws_sagemaker_invoke_endpointparameter== parameter and passing the name of the SageMaker endpoint.  

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


## 7. Execute the function and observe predictions
Now that we have the function created linking back to the SageMaker endpoint, we can pass it values and observer predictions. In this example, we will observe that based on the values passed, we are predicting that particular this customer **will churn**. This is represented by the **"True"** result in the **‘Will Churn?’** column as shown in the screenshot.

``` sql
select 
will_churn('IN',65,415,'no','no',0,129.1,137,228.5,83,208.8,111,12.7,6,4) as 'Will Churn?';

```

<span class="image">![Reader Load](/ml/sagemaker/1-sagemaker-out.png?raw=true)</span>



To continue the example, we will compare the training data with the SageMaker models predicted outputs. The table churn, already contains the actual churn or not churn results in the last column. We will compare these results with the predicted results using the function, by executing following query. 

``` sql
SELECT count(*) as "Predicted to Churn", 
	SUM(case when Churn  like "True%" then 1 else 0 end) as "Did Churn",
	SUM(case when Churn  like "False%" then 1 else 0 end) as "Did Not Churn",
	round(100.0 * 
	SUM(case when Churn  like "True%" then 1 else 0 end)/count(*), 2) as "Accuracy %"
FROM churn
WHERE will_churn(state, acc_length,
       area_code, int_plan,
       vmail_plan, vmail_msg,
       day_mins, day_calls,
       eve_mins, eve_calls,
       night_mins, night_calls,
       int_mins, int_calls,
       cust_service_calls) like 'True%';  
```

You can observe that based on the following output, our Sagemake model is 98.75% accurate.

<span class="image">![Reader Load](/ml/sagemaker/2-sagemaker-function-out.png?raw=true)</span>


Exit from the mysql prompt by running command below, before you proceed to the next section.

``` sql
exit
```
