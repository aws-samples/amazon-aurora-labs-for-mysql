# Use Comprehend with Aurora

<a href="https://aws.amazon.com/comprehend/" target="_blank">Amazon Comprehend</a> is a natural language processing (NLP) service that uses machine learning to find insights and relationships in text. No machine learning experience required. This lab will walk you through the process of integrating Aurora with the Comprehend Sentiment Analysis API and making sentiment analysis inferences via SQL commands.

This lab contains the following tasks:

1. Create an IAM role to allow Aurora to interface with Comprehend
2. Associate the IAM role with the Aurora DB cluster
3. Add the IAM role to the DB cluster parameter group and apply it
4. Run Comprehend inferences from Aurora

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/) (choose **Yes** for the **Enable Aurora ML Labs?** feature option)
* [Connect to the Cloud9 Desktop](/prereqs/connect/)
* [Create a New DB Cluster](/provisioned/create/) (conditional, only if you plan to create a cluster manually)
* [Overview and Prerequisites](/ml/overview/)


## 1. Create an IAM role to allow Aurora to interface with Comprehend

If you have not already opened a terminal window in the Cloud9 desktop in a previous lab, please [following these instructions](/prereqs/connect/) to do so now. Once connected, run the commands below, they will create an IAM role, and access policy.

```
aws iam create-role --role-name auroralab-comprehend-access \
--assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"rds.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"

aws iam put-role-policy --role-name auroralab-comprehend-access --policy-name inline-policy \
--policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":[\"comprehend:DetectSentiment\",\"comprehend:BatchDetectSentiment\"],\"Resource\":\"*\"}]}"
```

<span class="image">![Create IAM Role](c9-iam-create-role.png?raw=true)</span>

## 2. Associate the IAM role with the Aurora DB cluster

Associate the role with the DB cluster by using following command:

```
aws rds add-role-to-db-cluster --db-cluster-identifier auroralab-mysql-cluster \
--role-arn $(aws iam list-roles --query 'Roles[?RoleName==`auroralab-comprehend-access`].Arn' --output text)
```

Next, run the following command and repeat until the output shows as **available**, before moving on to the next step.

```
aws rds describe-db-clusters --db-cluster-identifier auroralab-mysql-cluster \
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Associate IAM Role](c9-rds-associate-role.png?raw=true)</span>


## 3. Add the IAM role to the DB cluster parameter group and apply it

Set the ==aws_default_comprehend_role== cluster-level parameter to the ARN of the IAM role we created in the first step of this lab. Run the following command:

```
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name $DBCLUSTERPG \
--parameters "ParameterName=aws_default_comprehend_role,ParameterValue=$(aws iam list-roles --query 'Roles[?RoleName==`auroralab-comprehend-access`].Arn' --output text),ApplyMethod=pending-reboot"
```

Reboot the DB cluster for the change to take effect. To minimize downtime use the manual failover process to trigger the reboot:

```
aws rds failover-db-cluster --db-cluster-identifier auroralab-mysql-cluster
```

Run the following command and wait until the output shows as **available**, before moving on to the next step:

```
aws rds describe-db-clusters --db-cluster-identifier auroralab-mysql-cluster \
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Reboot Wait Available](c9-rds-failover-wait.png?raw=true)</span>


## 4. Run Comprehend inferences from Aurora

Run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster to connect to the database:

```shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mltest
```

Aurora has a built-in Comprehend function which will make a call to the Comprehend service. It will pass the inputs of the `aws_comprehend_detect_sentiment` function, in this case the values of the `comment_text` columns in the `comments` table, to the Comprehend service and retrieve sentiment analysis results.

Run the following SQL query to run sentiment analysis on the comments table.

```sql
SELECT comment_text,
aws_comprehend_detect_sentiment(comment_text, 'en') AS sentiment,
aws_comprehend_detect_sentiment_confidence(comment_text, 'en') AS confidence
FROM comments;
```

You should see result as shown in the screenshot below. Observe the columns `sentiment`, and `confidence`. The combination of these two columns provide the inferred sentiment for the text in the `comment_text` column, and also the confidence score of the inference.

<span class="image">![Comprehend Query](c9-comprehend-query.png?raw=true)</span>

Disconnect from the DB cluster, using:

```sql
quit;
```
