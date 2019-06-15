# Connecting, Loading Data and Auto Scaling

This lab will walk you through the process of connecting to the DB cluster you have just created, and using the cluster for the first time. At the end you will test out in practice how Aurora read replica auto scaling works in practice using a load generator script. This lab contains the following tasks:

1. Connecting to your workstation EC2 instance
2. Connecting to the DB cluster
3. Loading an initial data set from S3
4. Running a read-only workload


## 1. Connecting to your workstation EC2 instance

For Windows users: We will use PuTTY and PuTTY Key Generator to connect to the workstation using SSH. If you do not have these applications already installed please use the instructions in the [Prerequisites](/modules/prerequisites/#3-install-an-ssh-client-windows-users) for setting up PuTTY and connecting via SSH.

For macOS or Linux users: You can connect using the following command from a terminal, however you will need to change the permissions of the certificate file first:

```
chmod 0600 /path/to/downloaded/labkeys.pem

ssh -i /path/to/downloaded/labkeys.pem ubuntu@[bastionEndpoint]
```


## 2. Connecting to the DB cluster

Connect to the Aurora database just like you would to any other MySQL-based database, using a compatible client tool. In this lab you will be using the `mysql` command line tool to connect. The basic command is as follows:

```
mysql -h [clusterEndpoint] -u [username] -p [password] [database]
```

If you have completed the previous lab, and created the Aurora DB cluster manually, you would input the **Cluster Endpoint** of that cluster as displayed at the end of that lab, along with the username, password and schema (database) you configured for that cluster in the parameter placeholders of the command above.

However, if you have skipped that lab and provisioned the cluster using the CloudFormation template, we have set the DB cluster's database credentials automatically for you, and have also created a schema named `mylab` as well. The credentials were saved to an <a href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html" target="_blank">AWS SecretsManager</a> secret. For your convenience, these credentials have been set as environment variables on the EC2 instance, although this practice should be avoided in a production system. Using these environment variables, you can connect to the database as follows:

```
mysql -h [clusterEndpoint] -u$DBUSER -p$DBPASS [database]
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually
--- | --- | --- | ---
-h | [clusterEndpoint] | See CloudFormation stack output | See previous lab
-u | [username] | `$DBUSER` | `masteruser` or manually set
-p | [password] | `$DBPASS` | Manually set
| [database] | `mylab` | `mylab` or manually set

!!! note
    You can view and retrieve the credentials stored in the secret using the following command:

    ```
    aws secretsmanager get-secret-value --secret-id [secretArn] | jq -r '.SecretString'
    ```


## 3. Loading an initial data set from S3

Once connected to the DB cluster, run the following SQL queries to create an initial table:

```
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

```
LOAD DATA FROM S3 MANIFEST
's3-eu-west-1://aurorareinvent2018/output.manifest'
REPLACE
INTO TABLE sbtest1
CHARACTER SET 'latin1'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n';
```

Data loading may take several minutes, you will receive a successful query message once it completes. When completed, exit the MySQL command line:

```
quit;
```


## 4. Running a read-only workload

Once the data load completes successfully, you can run a read-only workload to generate load on the cluster. You will also observe the effects on the DB cluster topology. For this step you will use the **Reader Endpoint** of the cluster. If you created the cluster manually, you can find the endpoint value as indicated at the end of that lab. If the DB cluster was created automatically for you the value can be found in your CloudFormation stack outputs.

1. Run the load generation script from the EC2 instance command line:

    ```
    python3 loadtest.py -e [readerEndpoint] -u [username] -p [password] -d [schema]
    ```

    Or, if the cluster was created automatically:

    ```
    python3 loadtest.py -h [readerEndpoint] -u $DBUSER -p $DBPASS -d mylab
    ```

    **Command parameter values at a glance:**

    Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually
    --- | --- | --- | ---
    -e | [readerEndpoint] | See CloudFormation stack output | See previous lab
    -u | [username] | `$DBUSER` | `masteruser` or manually set
    -p | [password] | `$DBPASS` | Manually set
    -d | [database] | `mylab` | `mylab` or manually set
    -t |  | 24 (default) | 24 (default)

2.	Open the <a href="https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2" target="_blank">Amazon RDS service console</a>.

    !!! warning "Region Check"
        Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

3.	Take note that the reader node is currently receiving load. It may take a minute or more for the metrics to fully reflect the incoming load.

4.	After several minutes return to the list of instances and notice that a new reader is being provisioned to your cluster.

5.	Once the new replica becomes available, note that the load distributes and stabilizes (it may take a few minutes to stabilize).

6.	You can now type `CTRL+C` at the EC2 instance command line to quit the load generator, if you wish to. After a while the additional reader will be removed automatically.
