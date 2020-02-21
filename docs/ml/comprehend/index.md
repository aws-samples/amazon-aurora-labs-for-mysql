# Comprehend on Amazon Aurora

This lab will walk you through the process of provisioning the infrastructure needed to create and call Comprehend function from Amazon Aurora.

## This lab contains following tasks:

1. Create IAM role required by Aurora to Talk to Comprehend.
2. Create and attach policy to the role.
3. Associate the IAM role with the Aurora cluster.
4. Add the Comprehend role to the db cluster parameter group.
5. Apply the new parameter to the database cluster.
6. Connect to the Aurora cluster and execute SQL commands to create and use Comprehend function.        

## 1. Create IAM role required by Aurora to Talk to Comprehend

If you are not already connected to the Session Manager workstation, please connect [following these instructions](/prereqs/connect/). Once connected, run the command below which will create the role.

``` shell
aws iam create-role --role-name $STACKNAME-ComprehendAuroraAccessRole-$STACKREGION \
--assume-role-policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"rds.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
```
 
## 2. Create and attach policy to the role

Run followings command to create a new policy and attach to the role we created in the last step.

``` shell
aws iam create-policy --policy-name $STACKNAME-ComprehendAuroraPolicy-$STACKREGION \
--policy-document "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Sid\":\"AllowAuroraToComprehendService\",\"Effect\":\"Allow\",\"Action\":[\"comprehend:DetectSentiment\",\"comprehend:BatchDetectSentiment\"],\"Resource\":\"*\"}]}"

aws iam attach-role-policy --role-name $STACKNAME-ComprehendAuroraAccessRole-$STACKREGION \
--policy-arn $(aws iam list-policies --query "Policies[?PolicyName=='$STACKNAME-ComprehendAuroraPolicy-$STACKREGION'].Arn" --output text)

```

## 3. Associate the IAM role with the Aurora cluster

Add the role to the list of associated roles for a DB cluster by using following commands.  

``` shell
aws rds add-role-to-db-cluster --db-cluster-identifier labstack-cluster \
--role-arn $(aws iam list-roles --query "Roles[?RoleName=='$STACKNAME-ComprehendAuroraAccessRole-$STACKREGION'].Arn" --output text)

```
Run the following command and wait until the output shows as **"available"**, before moving on to the next step.

``` shell
aws rds describe-db-clusters --db-cluster-identifier labstack-cluster \
--query 'DBClusters[*].[Status]' --output text
```

<span class="image">![Reader Load](/ml/comprehend/2-dbcluster-available.png?raw=true)</span>

## 4. Add the Comprehend role to the db cluster parameter group

Set the ==aws_default_comprehend_role== cluster-level parameter to thw Comprehend IAM role we created in the first step of this lab. We will use the ARN value of the IAM role. Execute the following command.

``` shell
aws rds modify-db-cluster-parameter-group \
--db-cluster-parameter-group-name $DBCLUSTERPG \
--parameters "ParameterName=aws_default_comprehend_role,ParameterValue=$(aws iam list-roles --query "Roles[?RoleName=='$STACKNAME-ComprehendAuroraAccessRole-$STACKREGION'].Arn" --output text),ApplyMethod=pending-reboot" 
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


## 6. Connect to the Aurora cluster and execute SQL commands to create and use Comprehend function

Run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. This will connect you to the Aurora MySQL instance.

``` shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mltest
```

Aurora has the built-in Comprehend function which will make a call to the Comprehend service, pass the comments from the table and return the appropriate results.
Run the following SQL query to run sentiment analysis on the comments table.

``` sql
SELECT comment_text,
aws_comprehend_detect_sentiment(comment_text, 'en') AS sentiment,
aws_comprehend_detect_sentiment_confidence(comment_text, 'en') AS confidence
FROM comments;
```

You should see the result as shown in the screenshot below. Observe the columns sentiment, and confidence. Combination of these two columns provide the sentiment for the text in the comment_text column, and also the confidence score of the prediction.

<span class="image">![Reader Load](/ml/comprehend/1-comprehend-query.png?raw=true)</span>

Exit from the mysql prompt by running command below, before you proceed to the next section.

``` sql
exit
```
