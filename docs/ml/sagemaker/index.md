<<<<<<< HEAD
This lab will walk you through the process of provisioning the infrastructure needed to create and call Comprehend function from Amazon Aurora.

## Pre-requisites
Before running the lab make sure you have met the following pre-requisites.

* [Complete the pre-requisites section](/prereqs/Overview/)
* [Complete Comprehend on Aurora lab](/ml/comprehend/)

## This lab contains following tasks:

1. Create IAM role required by Aurora to Talk to Sagemaker.
2. Create and attach policy to the role.
3. Associate the IAM role with the Aurora cluster.
4. Add the Sagemaker role to the db cluster parameter group.
5. Apply the new parameter to the database cluster.
6. Create the SageMaker function.
7. Execute the function and observe predictions.  


## 1. Create IAM role required by Aurora to Talk to Sagemaker

If you are not already connected to the Session Manager workstation command line from previous labs, please connect [following these instructions](/prereqs/connect/). Once connected, run the commands below.

``` shell
aws iam create-role --role-name SagemakerAuroraAccessRole \
--assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"rds.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
```

## 2. Create and attach policy to the role

We will download the policy file, update it with the sagmaker endpoint, and then attach the policy to the role using following commands.

``` shell

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
=======
# Using SageMaker with Aurora

<a href="https://aws.amazon.com/sagemaker/" target="_blank">Amazon SageMaker</a> is a fully managed service that provides every developer and data scientist with the ability to build, train, and deploy machine learning (ML) models quickly. This lab will walk you through the process of integrating Aurora with SageMaker Endpoints to infer customer churn in a data set using SQL commands.

This lab contains the following tasks:

1. Create an IAM role to allow Aurora to interface with SageMaker
2. Associate the IAM role with the Aurora DB cluster
3. Add the IAM role to the DB cluster parameter group and apply it
4. Create a SageMaker integration function in Aurora
5. Run SageMaker inferences from Aurora

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/) - choose **Yes** for the **Enable Aurora ML Labs?** feature option
* [Connect to the Session Manager Workstation](/prereqs/connect/)
* [Overview and Prerequisites](/ml/overview/)

## 1. Create an IAM role to allow Aurora to interface with SageMaker

If you are not already connected to the Session Manager workstation, please connect [following these instructions](/prereqs/connect/). Once connected, run the command below which will create an IAM role, and access policy.

```shell
aws iam create-role --role-name auroralab-sagemaker-access \
--assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"rds.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"

sed -i "s%EndpointArn%$(aws sagemaker describe-endpoint --endpoint-name auroraml-churn-endpoint --query [EndpointArn] --output text)%" sagemaker_policy.json

aws iam put-role-policy --role-name auroralab-sagemaker-access --policy-name inline-policy \
--policy-document file://sagemaker_policy.json
```

## 2. Associate the IAM role with the Aurora DB cluster

Associate the role with the DB cluster by using following command:

```shell
aws rds add-role-to-db-cluster --db-cluster-identifier auroralab-mysql-cluster \
--role-arn $(aws iam list-roles --query 'Roles[?RoleName==`auroralab-sagemaker-access`].Arn' --output text)
```		

Run the following command and wait until the output shows as **available**, before moving on to the next step.

```shell
aws rds describe-db-clusters --db-cluster-identifier auroralab-mysql-cluster \
>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Reader Load](/ml/comprehend/2-dbcluster-available.png?raw=true)</span>

<<<<<<< HEAD
## 4. Add the Sagemaker role to the db cluster parameter group

``` shell
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name $DBCLUSTERPG \
--parameters "ParameterName=aws_default_sagemaker_role,ParameterValue=$(aws iam list-roles --query 'Roles[?RoleName==`SagemakerAuroraAccessRole`].Arn' --output text),ApplyMethod=pending-reboot"
```

## 5. Apply the new parameter to the database cluster.
Reboot the cluster for the change to take effect by executing the commands below. Replacing the ==[dbCluster]== placeholder with the  name of your DB cluster.

``` shell
aws rds failover-db-cluster --db-cluster-identifier [dbCluster]
```
Run the following command and wait until the output shows as **"available"**, before moving on to the next step.  Replacing the ==[dbCluster]== placeholder with the name of your DB cluster.

``` shell
aws rds describe-db-clusters --db-cluster-identifier [dbCluster] \
=======
## 3. Add the IAM role to the DB cluster parameter group and apply it

Set the ==aws_default_sagemaker_role== cluster-level parameter to the ARN of the IAM role we created in the first step of this lab. Run the following command:

```shell
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name $DBCLUSTERPG \
--parameters "ParameterName=aws_default_sagemaker_role,ParameterValue=$(aws iam list-roles --query 'Roles[?RoleName==`auroralab-sagemaker-access`].Arn' --output text),ApplyMethod=pending-reboot"
```

Reboot the DB cluster for the change to take effect. To minimize downtime use the manual failover process to trigger the reboot:

```shell
aws rds failover-db-cluster --db-cluster-identifier auroralab-mysql-cluster
```

Run the following command and wait until the output shows as **available**, before moving on to the next step:

```shell
aws rds describe-db-clusters --db-cluster-identifier auroralab-mysql-cluster \
>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Reader Load](/ml/comprehend/2-dbcluster-available.png?raw=true)</span>

<<<<<<< HEAD

## 6.Create Sagemaker function

Execute the commands below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. This will connect you to the Aurora MySQL  instance.

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


## 7. Execute the function and observe predictions
Now that we have the function created linking back to the sagemaker endpoint, we can pass it values and observer predictions. In this example, we will observe that based on the values passed, we are predicting that particular this customer **will churn**. This is represented by the **"True"** result in the **‘Will Churn?’** column as shown in the screenshot.

``` sql
select 
will_churn('IN',65,415,'no','no',0,129.1,137,228.5,83,208.8,111,12.7,6,4) as 'Will Churn?';

=======
## 4. Create a SageMaker integration function in Aurora

Run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster to connect to the database:

```shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mltest
```

Once connected, execute the following SQL query to create the **will_churn** function in the database, using the ==alias aws_sagemaker_invoke_endpoint== parameter and passing the name of the SageMaker endpoint.  

??? tip "What is a SageMaker Endpoint?"
	To simplify the Aurora labs, a SageMaker model has been trained and deployed automatically for you. These resources were deployed when you selected **Yes** for the **Enable Aurora ML Labs?** feature option when you deployed the labs environment using CloudFormation.

	Amazon SageMaker also provides model <a href="https://docs.aws.amazon.com/sagemaker/latest/dg/how-it-works-hosting.html" target="_blank">hosting services</a> for model deployment. Amazon SageMaker provides an HTTPS endpoint where your machine learning model is available to provide inferences.



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
 cust_service_calls bigint(20)
) RETURNS varchar(2048) CHARSET latin1
alias aws_sagemaker_invoke_endpoint
endpoint name 'auroraml-churn-endpoint';
```

5. Run SageMaker inferences from Aurora

Now that we have an integration function linking back to the SageMaker endpoint, the DB cluster can pass values to SageMaker and retrieve inferences. In this example, we will submit values from the `churn` table as function inputs to determine if a particular customer **will churn**. This is represented by the **"True"** result in the **‘Will Churn?’** column as shown in the screenshot.

```sql
SELECT
will_churn('IN',65,415,'no','no',0,129.1,137,228.5,83,208.8,111,12.7,6,4) as 'Will Churn?';
>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
```

<span class="image">![Reader Load](/ml/sagemaker/1-sagemaker-out.png?raw=true)</span>

<<<<<<< HEAD


To continue the example, we will compare the training data with the SageMaker models predicted outputs. The table churn, already contains the actual churn or not churn results in the last column. We will compare these results with the predicted results using the function, by executing following query. 

``` sql
SELECT count(*) as "Predicted to Churn", 
	SUM(case when Churn  like "True%" then 1 else 0 end) as "Did Churn",
	SUM(case when Churn  like "False%" then 1 else 0 end) as "Did Not Churn",
	round(100.0 * 
=======
To continue the example, we will compare the training data with the SageMaker model's outputs. The `churn` table already contains the actual churn outcomes for particular customers. We will compare these results with the inferred results using the function to understand the model's effectiveness, by executing following query:

```sql
SELECT count(*) as "Predicted to Churn",
	SUM(case when Churn  like "True%" then 1 else 0 end) as "Did Churn",
	SUM(case when Churn  like "False%" then 1 else 0 end) as "Did Not Churn",
	round(100.0 *
>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
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

<<<<<<< HEAD
You can observe that based on the following output, our Sagemake model is 99.25% accurate.

<span class="image">![Reader Load](/ml/sagemaker/2-sagemaker-function-out.png?raw=true)</span>
=======
Based on the query result, this SageMaker model is 99.25% accurate.

<span class="image">![Reader Load](/ml/sagemaker/2-sagemaker-function-out.png?raw=true)</span>

Disconnect from the DB cluster, using:

```sql
quit;
```
>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
