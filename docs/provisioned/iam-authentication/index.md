# IAM Authentication to access the DB Cluster

To connect to and use a database you need a user account within the database. This database user usually is required to use a password to restrict access. Within the database the database user is granted permissions to perform tasks. In general it is:

a) not recommended to store database credentials within an application

b) required to update/rotate credentials periodically

This lab will walk you through one option to address the typical challenges involved in working with database credentials. You will explore the use of IAM authentication to completely avoid the usage of database passwords or the need of rotating credentials. Instead behind the scenes short lived credentials will be leveraged. You will use an AWS Lambda function as an example to demonstrate how it works, but you can extend this example easily to EC2 instances or any other services that can assume a role. Of course, you can also use IAM Authentication for IAM users or groups.

This lab requires the following lab modules to be completed first:

- [Get Started](/prereqs/environment/) (you do not need to provision a DB cluster automatically)
- [Connect to the Cloud9 Desktop](/prereqs/connect/)

## 1. Create new database user and grant permissions
You will connect to the Aurora database just like you would do with any other MySQL-based database, using a compatible client tool like `mysql`. To find the clusterEndpoint see [Retrieve the DB cluster endpoints](/provisioned/create/#2-retrieve-the-db-cluster-endpoints).

If you have not already opened a terminal window in the Cloud9 Desktop in a previous lab, please [follow these instructions](/prereqs/connect/) to do so now.

!!! warning "Check for correct cluster endpoint"
    Make sure you take the endpoint of the **cluster** and not of the writer or reader instances.

During this lab we will use a secure connection to ensure encryption in transit. To do so you first need to download the required certificates first. Use the following command to download the RDS-related certificates as bundle into the current directory:

```
wget https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem
```

To connect to the cluster you can use the next command. The environment variables were already set during the cluster setup:

```
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" --ssl-ca=rds-combined-ca-bundle.pem
```

Once connected to the Aurora database, use the command below to create a database user account that uses an **AWS authentication token** instead of a password. In this lab we will use `user_app1` as dbusername, but you can use a different name accordingly. Run the following SQL query:

```
CREATE USER user_app1 IDENTIFIED WITH AWSAuthenticationPlugin as 'RDS';
```

??? info "How does this work?"
    Amazon RDS contains the AWSAuthenticationPlugin. This plugin takes an authentication token that is passed as the password. An authentication token is a unique string of characters that Amazon Aurora generates on request. Authentication tokens are generated using <a href="https://docs.aws.amazon.com/general/latest/gr/signing_aws_api_requests.html" target="_blank">AWS Signature Version 4</a>. Each token has a lifetime of 15 minutes. You don't need to store user credentials in the database, because authentication is managed externally using IAM. The required IAM policy will be introduced in the following steps. The token is **only used for authentication** and doesn't affect the session after it is established.

Run the following command to allow the just created database user account to connect to the cluster from anywhere but require using SSL:

```
GRANT USAGE ON *.* TO 'user_app1'@'%' REQUIRE SSL;
```

Now, grant the user permissions to create and drop tables, insert and selecting records within the database `mylab`. This will be needed later on for some testing.

```
GRANT CREATE, INSERT, SELECT, DROP ON mylab.* TO 'user_app1'@'%';
```

<span class="image">![Create database user account](1-database-create-user-account.png?raw=true)</span>

You can now quit the connection
```
\q
```


## 2. Create IAM policy that maps to the database user account

To enable authentication for a certain user, role or group an IAM policy is required. Follow the steps to create an IAM policy, that grants the `rds-db:connect` action in connection with the database user `user_app1`.

Open the <a href="https://console.aws.amazon.com/iamv2/home" target="_blank">IAM console</a>.

Choose **Policies** from the left navigation pane.

Click **Create Policy**

<span class="image">![Create policy to allow connecting to the database](1-create-policy.png?raw=true)</span>

Select the JSON tab, past in the following policy and replace the parameters

* [ ] `region`, 
* [ ] `account-id` and 
* [ ] `DbiResourceId` 

with the appropriate values of your setup.

??? tip "What are these parameters for and where can they be found?"
    You will create a policy that allows to connect to a specific database instance `DbiResourceId` in a certain `region` within a specific `account-id`.
    The `account-id` can be found if you click on your username on the top right corner of the console as Account ID. The `region` is the same where you have deployed the database cluster. The `DbiResourceId` is displayed in the Configuration tab for your regional cluster as Resource ID.
    <span class="image">![DbiResourceId can be found under the configuration tab](2-cluster-dbi-resource-id.png?raw=true)</span>

!!! warning "Check for the correct DbiResourceId"
    The DbiResourceId must be the one from the **cluster** and not from the instances. You can verify that, by checking that the DbiResourceId starts with `cluster-`.

```
{
   "Version": "2012-10-17",
   "Statement": [
      {
         "Effect": "Allow",
         "Action": [
             "rds-db:connect"
         ],
         "Resource": [
             "arn:aws:rds-db:<region>:<account-id>:dbuser:<DbiResourceId>/user_app1"
         ]
      }
   ]
}
```

Click **Next: Tags**

<span class="image">![Input JSON for policy to allow connecting to the database](1-create-policy-json.png?raw=true)</span>

Click **Next: Review**

For **Name** enter a policy name, e.g. `auroralab-iam-auth-user_app1` and click **Create policy**

<span class="image">![Name the policy and create](1-create-policy-name.png?raw=true)</span>

This policy now can be attached to a user or role in order to allow connecting to the database cluster as `user_app1` using IAM authentication.

## 3. Create AWS Lambda function to test IAM authentication

Now, the database user account is created and a policy with the `rds-db:connect` permission to allow connecting to the Aurora Cluster as `user_app1`. What about having a test with a simple AWS Lambda function. You will create the Lambda function and test it first without using the policy and expecting it to fail. Afterwards you'll test it again with the policy attached and see what happens.

Open the <a href="https://console.aws.amazon.com/lambda/home" target="_blank">AWS Lambda console</a>.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Click **Create function**

<span class="image">![Create new Lambda Function](3-create-lambda.png?raw=true)</span>

Select **Author from scratch**

Enter a **Function name**, e.g. `auroralab-mysql-app1`

Select Python 3.9 as **Runtime**

<span class="image">![Create new Lambda Function - Options and basic information](3-create-lambda-basic.png?raw=true)</span>

Under **Advanced settings** activate **Enable VPC**

- Select the `auroralab-vpc`
- For subnets select the three private `auroralab-prv-sub-x`
- And as for security group pick `auroralab-workstation-sg`

??? info "Why enabling VPC?"
    Since the Aurora cluster is deployed within a private subnet, we need to instanciate our Lambda function within the same VPC to allow for connectivity. Also we select the security group `auroralab-workstation-sg` that does not allow any inbound connection, but all outgoing connections.

Click **Create function**

<span class="image">![Create new Lambda Function - Advanced settings](3-create-lambda-advanced.png?raw=true)</span>

Congratulations, the empty Lambda function was created. 

Now, change over to the Cloud9 session and open a terminal if the previous isn't open anymore. Use the following commands to create a new directory and cd into it.
```
cd ~/environment
mkdir auroralab-mysql-app1
cd auroralab-mysql-app1
```

Now, use the following to create the file of the Lambda function.
```
cat << EOF > lambda_function.py
import os
import sys
import logging
import boto3
import pymysql

# rds settings
host = os.environ["cluster_endpoint"]
username = os.environ["db_username"]
db_name = os.environ["db_name"]
port = 3306

# construct SSL
ssl = {"ca": "rds-combined-ca-bundle.pem"}

logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = boto3.client("rds")
token = client.generate_db_auth_token(host, port, username)

try:
    conn = pymysql.connect(
        host=host,
        port=port,
        user=username,
        password=token,
        database=db_name,
        charset="utf8",
        ssl=ssl,
        connect_timeout=5,
    )
except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to Aurora MySQL instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to Aurora MySQL instance succeeded")


def lambda_handler(event, context):
    """
    This function performs the test with the Aurora MySQL instance
    """

    item_count = 0
    with conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE Employee ( EmpID int NOT NULL, Name varchar(255) NOT NULL, PRIMARY KEY (EmpID))"
        )
        logger.info("Created table in Aurora MySQL database")
        cur.execute('INSERT INTO Employee (EmpID, Name) VALUES (1, "Joe")')
        cur.execute('INSERT INTO Employee (EmpID, Name) VALUES (2, "Bob")')
        cur.execute('INSERT INTO Employee (EmpID, Name) VALUES (3, "Mary")')
        conn.commit()
        cur.execute("SELECT * FROM Employee")
        for row in cur:
            item_count += 1
            logger.info(row)
        conn.commit()
        logger.info("Added %d items to Aurora MySQL table" % (item_count))
        cur.execute("DROP TABLE Employee")
    conn.commit()
    logger.info("Dropped table from Aurora MySQL database")

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": "Testing access successful. Created Table, added %d items to table, and dropped table."
        % (item_count),
    }
EOF
```

Since the `pymysql` package is not included by default you need to create a package that contains it. In this lab the necessary steps will be provided, but check [Deploy Python Lambda functions with .zip file archives](https://docs.aws.amazon.com/lambda/latest/dg/python-package.html) if you are interested in more details.

Install the required package `pymysql` and create a deployment package together with the rds certificates to allow a secure connection.

```
pip install --target ./package pymysql
cd package
zip -r ../auroralab-mysql-app1-deployment-package.zip .
cd ..
cp ~/environment/rds-combined-ca-bundle.pem .
zip -g auroralab-mysql-app1-deployment-package.zip lambda_function.py rds-combined-ca-bundle.pem
```

Now, deploy the function using the [AWS Command Line Interface](https://aws.amazon.com/cli/).

```
aws lambda update-function-code --function-name auroralab-mysql-app1 --zip-file fileb://auroralab-mysql-app1-deployment-package.zip
```

Your output should look similar to the following
<span class="image">![Lambda packaging and deployment](3-lambda-packaging-deployment.png?raw=true)</span>

As a last step you need to add the environment variables for the cluster endpoint, the database and the database user. You can use the following command to add them to the Lambda function.

```
aws lambda update-function-configuration --function-name auroralab-mysql-app1 --environment Variables="{db_name=mylab,db_username=user_app1,cluster_endpoint=`aws rds describe-db-cluster-endpoints --query "DBClusterEndpoints[?EndpointType=='WRITER'].Endpoint" --output text | grep auroralab-mysql-cluster`}"
```
<span class="image">![Lambda packaging and deployment](3-lambda-update-env-vars.png?raw=true)</span>

## 4. Test database access without attached IAM policy

In order to test the authentication, you will create a test event with which the lambda function will be triggered. The content of the event doesn't matter since we do not need any input to perform this simple test.

Open the <a href="https://console.aws.amazon.com/lambda/home" target="_blank">AWS Lambda console</a>.

Click on the Lambda function `auroralab-mysql-app1`

Select the tab **Test**

Click the button **Test**. Since the function here, does not react on an events payload, we can leave the default event data.

<span class="image">![Lambda execution test](4-lambda-execution-test.png?raw=true)</span>

The execution should fail with a similar error notification like the following.

<span class="image">![Lambda execution failed](4-lambda-execution-failed.png?raw=true)</span>

The execution failed, since the role that is attached to the Lambda function has not the required permissions to connect to the cluster.

## 5. Test database access again with IAM policy attached

Now, let's fix that by attaching the previously created policy to the Lambda functions execution role.

Open the <a href="https://console.aws.amazon.com/iamv2/home" target="_blank">IAM console</a>.

Choose **Roles** from the left navigation pane and search for `mysql-app1`

Click on the role starting with `auroralab-mysql-app1-role`

<span class="image">![Select role of the Lambda function](5-select-role.png?raw=true)</span>

With the role opened click **Add permissions** and choose **Attach policies**

<span class="image">![Select role of the Lambda function](5-add-permissions.png?raw=true)</span>

Now, activate the checkbox for the policy `auroralab-iam-auth-user_app1` which should be quite on top of the list

<span class="image">![Attach policy](5-attach-policy.png?raw=true)</span>

Finish the step by clicking **Attach policies** on the bottom of the page.

Next go back to the Lambda console, force an update and test again. Since the authentication tokens are valid up to 15 min we want to avoid the reuse of that token and instead make sure a new token will be issued. You will force an update of the Lambda function by updating the execution timeout to 4 seconds before conducting the new test.

Open the <a href="https://console.aws.amazon.com/lambda/home" target="_blank">AWS Lambda console</a>.

Click on the Lambda function `auroralab-mysql-app1`

Select the tab **Configuration**

Under **General configuration** click **Edit**

<span class="image">![Lambda update configuration](5-lambda-update-configuration.png?raw=true)</span>

Change `Timeout` to 4 seconds and click **Save**

<span class="image">![Lambda change timeout to 4 sec](5-lambda-change-timeout.png?raw=true)</span>

Select the tab **Test** as in the step before.

Click the button **Test**. Again, you can leave the default event data.

This time the execution will succeed because the execution role of the Lambda function now has the required permission to connect to the cluster as the user `user_app1` and because you have granted the neccessary permissions within the cluster to the user `user_app1`

<span class="image">![Lambda execution succeeded](5-lambda-execution-succeeded.png?raw=true)</span>


## 6. Check the error log for unauthorized access

Well, you have tried to connect to the Aurora cluster with and without permission. The question is, can this be seen within the logs? Yes, go and have a look yourself.

Open the <a href="https://console.aws.amazon.com/cloudwatch/" target="_blank">Amazon CloudWatch console</a> 

On the left side in the menu under **Logs** click **Log groups**

Choose the log group starting with `/aws/rds/cluster/auroralab-mysql-cluster` and ending with `/error`

Click on **Search all**

<span class="image">![Search all in log groups](6-search-all.png?raw=true)</span>

Now, filter for `denied`

<span class="image">![Filter in log groups for denied](6-filter-denied.png?raw=true)</span>

You should see at least one entry stating `Access denied` for the user `user_app1`. What can be built on top of that will be explored in the next step.


## 7. Setup an alarm to get notified on failed logins

Another step to enhance security could be not only to monitor login attempts but to alarm in case of any failed login. You will now add a simple alarm based on the CloudWatch Logs for the audit log. To do so, you will create a metric filter for a log roup.

??? tip "What is a metric filter?"
    Using a metric filter you can search and filter log data to turn it into numerical CloudWatch metrics. These metrics then can be used to set an alarm or a graph.
    Important to know is, that this doesn't work for logs in the past.
    Further information can be found in the <a href="https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/MonitoringLogData.html" target="_blank">Amazon CloudWatch Logs documentation</a>.

Open the <a href="https://console.aws.amazon.com/cloudwatch/" target="_blank">Amazon CloudWatch console</a> 

On the left side in the menu under **Logs** click **Log groups**

Choose the log group starting with `/aws/rds/cluster/auroralab-mysql-cluster` and ending with `/error`

Under **Actions** select **Create metric filter**

For **Filter pattern** use `Access denied`

To test the filter pattern select a log stream from the combobox and click **Test pattern**.

Click **Next**

<span class="image">![Create metric filter](1-alarm-create-metric-filter.png?raw=true)</span>

Enter a name for the filter `AuroraLabAccessDeniedFilter`

For **Metric namespace**, enter a name where the metric will be published `AuroraLab`

For **Metric name**, enter a name `MysqlCluster-AccessDenied` to identify this specific metric within the namespace

For **Metric value** enter 1, since only the occurences should be counted

Leave **Default value** empty, so no value will be published

For **Unit** select `Count`

Click **Next**

<span class="image">![Create metric filter - Assign metric](7-alarm-assign-metric.png?raw=true)</span>

Confirm the review by clicking **Create metric filter**

Now the metric filter is created and the alarm can be created an top of it. Select the Metric filter and click **Create alarm**

<span class="image">![Create alarm for metric filter](7-alarm-create-for-metric-filter.png?raw=true)</span>

For the **Metric** select a Period of 1 minute

Under **Conditions** leave the defaults to `Static` and `Greater`. Then choose the threshold value of 0 to trigger the alarm whenever a value greater then 0 is monitored

Click **Next**

<span class="image">![Create alarm for metric filter](7-alarm-specify-conditions.png?raw=true)</span>

In this step we will setup an action that should be taken when the alarm gets triggered. In this lab we'll choose a notification that will be sent out to an email address.

Choose **Create new topic**

Leave the topic name as its default and enter a valid email address

To finish the setup of the new topic click **Create topic**

Click **Next**

<span class="image">![Create alarm for metric filter](1-alarm-setup-notification.png?raw=true)</span>

Click **Next**

Give the alarm a name and enter `AuroraLab access denied`

Click **Next**

<span class="image">![Create alarm for metric filter](1-alarm-add-name.png?raw=true)</span>

Check the preview and click **Create alarm**

The alarm might start with a state of `Insufficient data`. That is expected, since the only data the alarm receives are counts of `Access denied` events. And right now, nobody tries to connect. Please note, the alarm won't react on old log entries.

Under actions you might see a warning, because the email subscription hasn't been confirmed yet. Check you mailbox and confirm the subscription to be able receiving notifications.

<span class="image">![Create alarm for metric filter](1-alarm-insufficient-data.png?raw=true)</span>

To produce a new access denied event go back to the Cloud9 Desktop and try to connect to the database with a wrong user and or wrong password.

```
CLUSTER_ENDPOINT=`aws rds describe-db-cluster-endpoints --query "DBClusterEndpoints[?EndpointType=='WRITER'].Endpoint" --output text | grep auroralab-mysql-cluster`
mysql -h$CLUSTER_ENDPOINT --enable-cleartext-plugin -u'user_app1' -pwrongpwd mylab
```

Give it a couple of minutes and check your mailbox for the notification mail. Once the alarm got triggered with our settings it takes around six minutes to change the state back to `Insufficient data`

<span class="image">![Alarm notification mail](7-alarm-notification.png?raw=true)</span>

## 8. Cleanup Ressources

```

```