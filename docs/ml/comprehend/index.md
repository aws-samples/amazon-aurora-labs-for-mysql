<<<<<<< HEAD
# Comprehend on Amazon Aurora

This lab will walk you through the process of provisioning the infrastructure needed to create and call Comprehend function from Amazon Aurora.

## This lab contains following tasks:

1. Create IAM role required by Aurora to Talk to Comprehend.
2. Create and attach policy to the role.
3. Associate the IAM role with the Aurora cluster.
4. Add the Comprehend role to the db cluster parameter group.
5. Apply the new parameter to the database cluster.
6. Connect to the Aurora cluster and execute SQL commands to create and use comprehend function.        

## 1. Create IAM role required by Aurora to Talk to Comprehend

If you are not already connected to the Session Manager workstation, please connect [following these instructions](/prereqs/connect/). Once connected, run the command below which will create the role.

``` shell
aws iam create-role --role-name ComprehendAuroraAccessRole \
--assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"rds.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
```
 
## 2. Create and attach policy to the role

Run followings command to create a new policy and attach to the role we created in the last step.

```
aws iam create-policy --policy-name ComprehendAuroraPolicy \
--policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AllowAuroraToComprehendService\",\"Effect\":\"Allow\",\"Action\":[\"comprehend:DetectSentiment\",\"comprehend:BatchDetectSentiment\"],\"Resource\":\"*\"}]}"

aws iam attach-role-policy --role-name ComprehendAuroraAccessRole \
--policy-arn $(aws iam list-policies --query 'Policies[?PolicyName==`ComprehendAuroraPolicy`].Arn' --output text)

```

## 3. Associate the IAM role with the Aurora cluster

Add the role to the list of associated roles for a DB cluster by using following commands. Replacing the ==[dbCluster]== placeholder with the name of your DB cluster. If  created the Aurora DB cluster manually, you would find the cluster name on the DB cluster details page in the RDS console. If you provisioned the DB cluster using the CloudFormation template, you can find the value for the cluster name parameter in the stack outputs. 

``` shell
aws rds add-role-to-db-cluster --db-cluster-identifier [dbCluster] \
--role-arn $(aws iam list-roles --query 'Roles[?RoleName==`ComprehendAuroraAccessRole`].Arn' --output text)

```
Run the following command and wait until the output shows as **"available"**, before moving on to the next step.  Replacing the ==[dbCluster]== placeholder with the name of your DB cluster.

``` shell
aws rds describe-db-clusters --db-cluster-identifier [dbCluster] \
=======
# Use Comprehend with Aurora

<a href="https://aws.amazon.com/comprehend/" target="_blank">Amazon Comprehend</a> is a natural language processing (NLP) service that uses machine learning to find insights and relationships in text. No machine learning experience required. This lab will walk you through the process of integrating Aurora with the Comprehend Sentiment Analysis API and making sentiment analysis inferences via SQL commands.

This lab contains the following tasks:

1. Create an IAM role to allow Aurora to interface with Comprehend
2. Associate the IAM role with the Aurora DB cluster
3. Add the IAM role to the DB cluster parameter group and apply it
4. Run Comprehend inferences from Aurora

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/) - choose **Yes** for the **Enable Aurora ML Labs?** feature option
* [Connect to the Session Manager Workstation](/prereqs/connect/)
* [Overview and Prerequisites](/ml/overview/)


## 1. Create an IAM role to allow Aurora to interface with Comprehend

If you are not already connected to the Session Manager workstation, please connect [following these instructions](/prereqs/connect/). Once connected, run the command below which will create an IAM role, and access policy.

```shell
aws iam create-role --role-name auroralab-comprehend-access \
--assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"rds.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"

aws iam put-role-policy --role-name auroralab-comprehend-access --policy-name inline-policy \
--policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"comprehend:DetectSentiment\",\"comprehend:BatchDetectSentiment\"],\"Resource\":\"*\"}]}"
```

## 2. Associate the IAM role with the Aurora DB cluster

Associate the role with the DB cluster by using following command:

```shell
aws rds add-role-to-db-cluster --db-cluster-identifier auroralab-mysql-cluster \
--role-arn $(aws iam list-roles --query 'Roles[?RoleName==`auroralab-comprehend-access`].Arn' --output text)

```

Run the following command and wait until the output shows as **available**, before moving on to the next step.

```shell
aws rds describe-db-clusters --db-cluster-identifier auroralab-mysql-cluster \
>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Reader Load](/ml/comprehend/2-dbcluster-available.png?raw=true)</span>

<<<<<<< HEAD
## 4. Add the Comprehend role to the db cluster parameter group

Set the ==aws_default_comprehend_role== cluster-level parameter to thw Comprehend IAM role we created in the first step of this lab. We will use the ARN value of the IAM role. Execute the following command.

``` shell
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name $DBCLUSTERPG \
--parameters "ParameterName=aws_default_comprehend_role,ParameterValue=$(aws iam list-roles --query 'Roles[?RoleName==`ComprehendAuroraAccessRole`].Arn' --output text),ApplyMethod=pending-reboot" 
```

## 5. Apply the new parameter to the database cluster.
Reboot the cluster for the change to take effect by executing the commands below. Replacing the ==[dbCluster]== placeholder with the  name of your DB cluster.

``` shell
aws rds failover-db-cluster --db-cluster-identifier [dbCluster]
```
Run the following command and wait until the output shows as **"available"**, before moving on to the next step.  Replacing the ==[dbCluster]== placeholder with the name of your DB cluster.

``` shell
aws rds describe-db-clusters --db-cluster-identifier [dbCluster] \
--query 'DBClusters[*].[Status]' --output text
```
<span class="image">![Reader Load](/ml/comprehend/2-dbcluster-available.png?raw=true)</span>


## 6. Connect to the Aurora cluster and execute SQL commands to create and use comprehend function

Run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. This will connect you to the Aurora MySQL instance.

``` shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mltest
```

Aurora has the built-in comprehend function which will make a call to the Comprehend service, pass the comments from the table and return the appropriate results.
=======
## 3. Add the IAM role to the DB cluster parameter group and apply it

Set the ==aws_default_comprehend_role== cluster-level parameter to the ARN of the IAM role we created in the first step of this lab. Run the following command:

```shell
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name $DBCLUSTERPG \
--parameters "ParameterName=aws_default_comprehend_role,ParameterValue=$(aws iam list-roles --query 'Roles[?RoleName==`auroralab-comprehend-access`].Arn' --output text),ApplyMethod=pending-reboot"
```

Reboot the DB cluster for the change to take effect. To minimize downtime use the manual failover process to trigger the reboot:

```shell
aws rds failover-db-cluster --db-cluster-identifier auroralab-mysql-cluster
```

Run the following command and wait until the output shows as **available**, before moving on to the next step:

```shell
aws rds describe-db-clusters --db-cluster-identifier auroralab-mysql-cluster \
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Reader Load](/ml/comprehend/2-dbcluster-available.png?raw=true)</span>


## 4. Run Comprehend inferences from Aurora

Run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster to connect to the database:

```shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mltest
```

Aurora has a built-in Comprehend function which will make a call to the Comprehend service. It will pass the inputs of the `aws_comprehend_detect_sentiment` function, in this case the values of the `comment_text` columns in the `comments` table, to the Comprehend service and retrieve sentiment analysis results.

>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
Run the following SQL query to run sentiment analysis on the comments table.

```sql
SELECT comment_text,
aws_comprehend_detect_sentiment(comment_text, 'en') AS sentiment,
aws_comprehend_detect_sentiment_confidence(comment_text, 'en') AS confidence
FROM comments;
```

<<<<<<< HEAD
You should see the result as shown in the screenshot below. Observe the columns sentiment, and confidence. Combination of these two columns provide the sentiment for the text in the comment_text column, and also the confidence score of the prediction.

<span class="image">![Reader Load](/ml/comprehend/1-comprehend-query.png?raw=true)</span>

Exit from the mysql prompt by running command below, before you proceed to the next section.

``` sql
exit
=======
You should see result as shown in the screenshot below. Observe the columns `sentiment`, and `confidence`. The combination of these two columns provide the inferred sentiment for the text in the `comment_text` column, and also the confidence score of the inference.

<span class="image">![Reader Load](/ml/comprehend/1-comprehend-query.png?raw=true)</span>

Disconnect from the DB cluster, using:

```sql
quit;
>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
```
