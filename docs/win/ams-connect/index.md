# Connect to your Aurora MySQL DB cluster

To interact with the Aurora database cluster, you will use an <a href="https://aws.amazon.com/ec2/" target="_blank">Amazon EC2</a> Linux instance that acts like a workstation to interact with the AWS resources in the labs on this website. All necessary software packages and scripts have been installed and configured on this EC2 instance for you. To ensure a unified experience, you will be interacting with this workstation using <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html" target="_blank">AWS Systems Manager Session Manager</a>. With Session Manager you can interact with your workstation directly from the management console, without the need to install any software on your own devices.

!!! note
    At this time, you have completed the Aurora PostgreSQL portion of this workshop. you may close the command line windows and tabs used for those labs, if you wish and to eliminate any confusion. The following Aurora MySQL labs use a different set of resources, in order to provide a consistent experience.

This lab contains the following tasks:

1. Note the CloudFormation resource chart
2. Connect to your workstation instance
3. Verify lab environment
4. Connect to the DB cluster
5. Load an initial data set from S3

This lab requires the following prerequisites:

* [Get Started](/win/)


## 1. Note the CloudFormation resource chart

At the end of the getting started step, you have retrieved the **Outputs** of your CloudFormation stack. For the following Aurora MySQL labs, you will need the following values for lab resources:

Resource name | Value
--- | ---
DB Subnet Group | Refer to: ==[dbSubnetGroup]== in the stack outputs
Security Group | Refer to: ==[dbSecurityGroup]== in the stack outputs
EC2 Workstation | Refer to: ==[bastionMySQL]== in the stack outputs
Cluster Endpoint | Refer to: ==[mysqlClusterEndpoint]== in the stack outputs
Reader Endpoint	| Refer to: ==[mysqlReaderEndpoint]== in the stack outputs
Load Generator Script | Refer to: ==[mysqlRunDoc]== in the stack outputs
DB name	| `mylab`
DB username	| Preset as environment variable `DBUSER`
DB password	| Preset as environment variable `DBPASS`


## 2. Connect to your workstation instance

Open the <a href="https://eu-west-1.console.aws.amazon.com/systems-manager/session-manager?region=eu-west-1" target="_blank">Systems Manager: Session Manager service console</a>. Click **Configure Preferences**.

!!! warning "Console Differences"
    The introduction screen with the **Configure Preferences** and **Start Session** buttons only appears when you start using Session Manager for the first time in a new account. Once you have started using this service the console will display the session listing view instead, and the preferences page is accessible by clicking on the **Preferences** tab. From there, click the **Edit** button if you wish to change settings.

<span class="image">![Session Manager](1-session-manager.png?raw=true)</span>

Click the **Start session** button.

<span class="image">![Start Session](1-start-session.png?raw=true)</span>

Please select the correct EC3 instance to establish a session with. The workstation is named `labstack-mysql-bastion`, select it and click **Start session**.

<span class="image">![Connect Instance](1-connect-session.png?raw=true)</span>

If you see a black command like terminal screen and a prompt, you are now connected to the workstation. Type the following command to use the correct user account and context for the labs:

```shell
sudo su -l ubuntu
```

## 3. Verify lab environment

Let's make sure your workstation has been configured properly. Type the following command in the Session Manager command line:

```shell
tail -n1 /debug.log
```

You should see the output: `* bootstrap complete, rebooting`, if that is not the output you see, please wait a few more minutes and retry.

## 4. Connect to the DB cluster

Connect to the Aurora database just like you would to any other MySQL-based database, using a compatible client tool. In this lab you will be using the `mysql` command line tool to connect.

If you are not already connected to the Session Manager workstation command line from previous labs, please connect [following these instructions](/prereqs/connect/). Once connected, run the command below, replacing the ==[mysqlClusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. If you have completed the previous lab, and created the Aurora DB cluster manually, you would find the cluster endpoint on the DB cluster details page in the RDS console. If you have skipped that lab and provisioned the DB cluster using the CloudFormation template, you can find the value for the cluster endpoint parameter in the stack outputs.


```shell
mysql -h[mysqlClusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```

??? tip "Can I see the AWS Secrets Manager credentials?"
    You can view and retrieve the credentials stored in the secret using the following command:

    ```shell
    aws secretsmanager get-secret-value --secret-id [secretArn] | jq -r '.SecretString'
    ```

Once connected to the database, use the code below to create a stored procedure we'll use later in the labs, to generate load on the DB cluster. Run the following SQL queries:

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS minute_rollup$$
CREATE PROCEDURE minute_rollup(input_number INT)
BEGIN
 DECLARE counter int;
 DECLARE out_number float;
 set counter=0;
 WHILE counter <= input_number DO
 SET out_number=SQRT(rand());
 SET counter = counter + 1;
END WHILE;
END$$
DELIMITER ;
```


## 5. Load an initial data set from S3

Once connected to the DB cluster, run the following SQL queries to create an initial table:

```sql
DROP TABLE IF EXISTS `sbtest1`;
CREATE TABLE `sbtest1` (
 `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
 `k` int(10) unsigned NOT NULL DEFAULT '0',
 `c` char(120) NOT NULL DEFAULT '',
 `pad` char(60) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `k_1` (`k`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
```

Next, load an initial data set by importing data from an Amazon S3 bucket:

```sql
LOAD DATA FROM S3 MANIFEST
's3-us-east-1://awsauroralabsmy-us-east-1/samples/sbdata/sample.manifest'
REPLACE
INTO TABLE sbtest1
CHARACTER SET 'latin1'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n';
```

Data loading may take several minutes, you will receive a successful query message once it completes. When completed, exit the MySQL command line:

```sql
quit;
```
