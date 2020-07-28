# Set up Database Activity Streams (DAS)

This lab will show you how to set up and leverage <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/DBActivityStreams.html" target="_blank">Aurora Database Activity Streams (DAS)</a>. Database activity streams provide a near real-time data stream of the database activity in your relational database. When you integrate database activity streams with third-party monitoring tools, you can monitor and audit database activity.

Database Activity Streams have the following limits and requirements:

1. Currently, these streams are supported only with Aurora with MySQL compatibility version 2.3, which is compatible with MySQL version 10.7.
2. They require use of AWS Key Management Service (AWS KMS) because the activity streams are always encrypted.

This lab contains the following tasks:

1. Create an AWS KMS customer managed key (CMK)
2. Configure Database Activity Streams
3. Generate database load
4. Read activity from the stream
5. Stop the activity stream

This lab requires the following prerequisites:

* [Get Started](/win/)
* [Connect to your Aurora MySQL DB cluster](/win/ams-connect/)



## 1. Create an AWS KMS customer managed key (CMK)

Database activity streams require a master key to encrypt the data key that in turn encrypts the database activity logged (see <a href="https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#enveloping" target="_blank">envelope encryption</a>). The default Amazon RDS master key can’t be used as the master key for DAS. Therefore, you need to create a new AWS KMS customer managed key (CMK) to configure the DAS.

Open the <a href="https://eu-west-1.console.aws.amazon.com/kms/home?region=eu-west-1#/kms/home" target="_blank">AWS Key Management Service (KMS) console</a>. Click **Create a key**.

<span class="image">![KMS Home](kms-home.png?raw=true)</span>

On the next screen under **Configure key** choose `Symmetric` for **Key type** and click **Next**.

<span class="image">![KMS Configure](kms-configure.png?raw=true)</span>

In the **Create alias and description** section, name the key `auroralab-mysql-das`. Provide the following description of the key:

```text
Amazon Aurora lab, CMK for Aurora MySQL Database Activity Streaming (DAS)
```

Then, click **Next**.

<span class="image">![KMS Labels](kms-labels.png?raw=true)</span>
If you are attending an AWS-hosted event (using AWS-provided hashes)

In the **Key administrators** section, select `TeamRole` and `OpsRole` as an administrator (you can search for the names to find them quicker). Check the box next to `TeamRole` and `OpsRole` click **Next**.

<span class="image">![KMS Administrators](kms-admins.png?raw=true)</span>

Similarly to above, in the section named **This account** select the `[stackname-wkstation-[region]`, `TeamRole` and `OpsRole` IAM roles, check the box next to them, and click **Next**.

If you are running the workshop on your own (in your own account), you do not need to choose `TeamRole` and `OpsRole` as Administrators.

Review the policy for accuracy and click **Finish**.

<span class="image">![KMS Review](kms-review.png?raw=true)</span>

Verify the newly created KMS key on the KMS dashboard.

<span class="image">![KMS Listing](kms-listing.png?raw=true)</span>


## 2. Configure Database Activity Streams



Database Activity Streams for Amazon Aurora with MySQL compatibility provides a near real-time stream of database activities in your relational database. When integrated with third party database activity monitoring tools, Database Activity Streams can monitor and audit database activity to provide safeguards for your database and help you meet compliance and regulatory requirements.

Solutions built on top of Database Activity Streams can protect your database from internal and external threats. The collection, transmission, storage, and processing of database activity is managed outside your database, providing access control independent of your database users and admins. Your database activity is asynchronously pushed to an encrypted Amazon Kinesis data stream provisioned on behalf of your Aurora cluster.


Open the <a href="https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2#database:id=auroralab-mysql-cluster;is-cluster=true" target="_blank">Amazon RDS service console at the cluster details page</a>. If you navigated to the RDS console by other means, click on the `auroralab-mysql-cluster` in the **Databases** section of the console.

From the **Actions** dropdown button, choose **Start activity stream**. The **Database Activity Stream** setup window appears:

<span class="image">![RDS Cluster Details](rds-cluster-detail-action.png?raw=true)</span>

Set the **Master key**, to the alias of the symmetric key created in the prior step. Choose **Apply immediately**, then click **Continue**.

<span class="image">![RDS Enable DAS](rds-das-confirm.png?raw=true)</span>

The **Status** column for the DB cluster will start showing **configuring-activity-stream**. Please wait until the cluster becomes **Available** again. You may need to refresh the browser page to get the latest status.

<span class="image">![RDS Cluster Configuring](rds-cluster-configuring.png?raw=true)</span>

Verify that DAS is enabled by clicking on the cluster named `auroralab-mysql-cluster` and toggle to the **Configuration** tab.

<span class="image">![RDS Cluster Configuration Details](rds-cluster-config-pane.png?raw=true)</span>

Note the **Resource id** and **Kinesis stream** values, you will need these value further in this lab.


## 3. Generate database load
You will use Percona's TPCC-like benchmark script based on sysbench to generate load. For simplicity we have packaged the correct set of commands in an <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html" target="_blank">AWS Systems Manager Command Document</a>. You will use <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html" target="_blank">AWS Systems Manager Run Command</a> to execute the test.

If you are not already connected to the Session Manager workstation command line, please connect [following these instructions](/prereqs/connect/). Once connected, enter one of the following commands, replacing the placeholders appropriately.

If you have completed the [Create a New DB Cluster](/provisioned/create/) lab, and created the Aurora DB cluster manually execute this command:

```shell
aws ssm send-command \
--document-name [loadTestRunDoc] \
--instance-ids [ec2Instance] \
--parameters \
clusterEndpoint=[clusterEndpoint],\
dbUser=$DBUSER,\
dbPassword="$DBPASS"
```

If AWS CloudFormation has provisioned the DB cluster on your behalf, and you skipped the **Create a New DB Cluster** lab, you can run this simplified command:

```shell
aws ssm send-command \
--document-name [loadTestRunDoc] \
--instance-ids [ec2Instance]
```

??? tip "What do all these parameters mean?"
    Parameter | Description
    --- | ---
    --document-name | The name of the command document to run on your behalf.
    --instance-ids | The EC2 instance to execute this command on.
    --parameters | Additional command parameters.

The command will be sent to the workstation EC2 instance which will prepare the test data set and run the load test. It may take up to a minute for CloudWatch to reflect the additional load in the metrics. You will see a confirmation that the command has been initiated.

<span class="image">![SSM Command](1-ssm-command.png?raw=true)</span>


## 4. Read activity from the stream

A python script with sample code to read the activity stream has already been saved on your EC2 workstation at this location `/home/ec2-user/das-script.py`.


```shell
python3 das-script.py -rn [REGION_NAME] -ri [RESOURCE_ID] -s [STREAM_NAME]
```

The script will read records from the stream, and print it out on the command line, you can use a tool, such as <a href="https://jsonformatter.org/" target=_blank">jsonformatter.org</a>, to format the JSON structure to be more readable.

<span class="image">![1-das-55](1-das-55.png?raw=true)</span>

Your output should look similar to the following example:

```json
{
   "type":"DatabaseActivityMonitoringRecord",
   "clusterId":"cluster-LFLK7QA4UVZ2UARHJWKULMWYNQ",
   "instanceId":"db-2Y3JIITE3NCVNI6YIQN5LIA564",
   "databaseActivityEventList":[      {
         "logTime":"2020-07-06 20:43:51.636563+00",
         "type":"record",
         "clientApplication":null,
         "pid":20555,
         "dbUserName":"rdsadmin",
         "databaseName":"mysql",
         "remoteHost":"localhost",
         "remotePort":"10944",
         "command":"QUERY",
         "commandText":"show status like \\\\\'server_aurora_das_%\\\\\'",
         "paramList":null,
         "objectType":"TABLE",
         "objectName":"",
         "statementId":2990,
         "substatementId":1,
         "exitCode":"0",
         "sessionId":"5",
         "rowCount":4,
         "serverHost":"auroralab-mysql-node-2",
         "serverType":"MySQL",
         "serviceName":"Amazon Aurora MySQL",
         "serverVersion":"MySQL 5.7.12",
         "startTime":"2020-07-06 20:43:51.636257+00",
         "endTime":"2020-07-06 20:43:51.636563+00",
         "transactionId":"0",
         "dbProtocol":"MySQL",
         "netProtocol":"TCP",
         "errorMessage":"",
         "class":"MAIN"
      
}
   
]
}
```

## 5. Stop the activity stream

Open the <a href="https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2#database:id=auroralab-mysql-cluster;is-cluster=true" target="_blank">Amazon RDS service console at the cluster details page</a>, if not already open. If the cluster is not already selected, choose **Databases** and click on the DB identifier with the cluster named `auroralab-mysql-cluster`.

Click on the **Actions** dropdown, and select **Stop activity stream**.

<span class="image">![RDS Cluster Stop](rds-cluster-detail-stop.png?raw=true)</span>

On the setup screen choose **Apply immediately** and click **Continue**. 

<span class="image">![RDS DAS Stop](rds-das-stop.png?raw=true)</span>

The status column on the RDS Database home page for the cluster will start showing `configuring-activity-stream`.
