# Comprehend on Amazon Aurora

This lab will walk you through the process of provisioning the inrastructure needed to create and call Comprehend function from Amazon Aurora.

## This lab contains following tasks:

1. Create IAM role required by Aurora to Talk to Comprehend.
2. Create and attach policy to the role.
3. Associate the IAM role with the Aurora cluster.
4. Create cluster parameter group.
5. Add the Comprehend role to the db cluster parameter group.
6. Associate the cluster parameter group to the Aurora cluster.
7. Connect to the Aurora cluster and execute SQL commands to create and use comprehend function.        

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
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Reader Load](2-dbcluster-available.png?raw=true)</span>


## 4. Create cluster parameter group

Cluster-level parameters are grouped into DB cluster parameter groups. Create a new DB cluster parameter group, by executing followin command.

``` shell
aws rds create-db-cluster-parameter-group --db-cluster-parameter-group-name AllowAWSAccessToMLServices \
--db-parameter-group-family aurora-mysql5.7 --description "Allow access to AWS SageMaker and AWS Comprehend"  
```

## 5. Add the Comprehend role to the db cluster parameter group

Set the ==aws_default_comprehend_role== cluster-level parameter to thw Comprehend IAM role we created in the first step of this lab. We will use the ARN value of the IAM role. Execute the following command.

``` shell
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name AllowAWSAccessToMLServices \
--parameters "ParameterName=aws_default_comprehend_role,ParameterValue=$(aws iam list-roles --query 'Roles[?RoleName==`ComprehendAuroraAccessRole`].Arn' --output text),ApplyMethod=immediate" 
```

## 6. Associate the cluster parameter group to the Aurora cluster
Modify the DB cluster to use the new DB cluster parameter group. Then, reboot the cluster for the change to take effect by executing the commands below. Replacing the ==[dbCluster]== placeholder with the  name of your DB cluster.

``` shell
aws rds modify-db-cluster --db-cluster-identifier [dbCluster] \
--db-cluster-parameter-group-name AllowAWSAccessToMLServices

aws rds failover-db-cluster --db-cluster-identifier [dbCluster]
```

## 7. Connect to the Aurora cluster and execute SQL commands to create and use comprehend function

Run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. This will connect you to the Aurora mysql  instance.

``` shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS"
```

Aurora has the built-in comprehend fuction which will make a call to the Comprehend service, pass the comments from the table and return the appropriate results.
Run the following SQL query to run sentiment analysis on the comments table.

```sql
SELECT comment_text,
aws_comprehend_detect_sentiment(comment_text, 'en') AS sentiment,
aws_comprehend_detect_sentiment_confidence(comment_text, 'en') AS confidence
FROM comments;
```

You should see the result as shown in the screenshot below. Observe the columns sentiment, and confidence. Combination of these two columns provide the sentiment for the text in the comment_text column, and also the confidence score of the prediction.

<span class="image">![Reader Load](1-comprehend-query.png?raw=true)</span>