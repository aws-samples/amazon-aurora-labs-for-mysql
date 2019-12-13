# Connecting, Loading Data and Auto Scaling

This lab will walk you through the process of connecting to the DB cluster you have just created, and using the cluster for the first time. At the end you will test out how Aurora read replica auto scaling works in practice using a load generator script.

This lab contains the following tasks:

1. Connecting to your workstation EC2 instance
2. Connecting to the DB cluster
3. Loading an initial data set from S3
4. Running a read-only workload

This lab requires the following lab modules to be completed first:

* [Prerequisites](/modules/prerequisites/)
* [Creating a New Aurora Cluster](/modules/create/) (conditional, if creating a cluster manually)

## 1. Connecting to your workstation EC2 instance

To interact with the Aurora database cluster, you will use an Amazon EC2 Linux instance that acts like a workstation for the purposes of the labs. All necessary software packages and scripts have been installed and configured on this EC2 instance for you. To ensure a unified experience, you will be interacting with this workstation using <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html" target="_blank">AWS Systems Manager Session Manager</a>. With Session Manager you can interact with your workstation directly from the management console.

Open the <a href="https://us-west-2.console.aws.amazon.com/systems-manager/session-manager?region=us-west-2" target="_blank">Systems Manager: Session Manager service console</a>. Choose the **Preferences** tab, then click **Edit**.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

<span class="image">![Session Manager](1-session-manager.png?raw=true)</span>

Check the box next to **Enable Run As support for Linux instances**, and enter `ubuntu` in the text field. This will instruct Session Manager to connect to the workstation using the `ubuntu` operating system user account. Click **Save**.

!!! note
    You will only need to set the preferences once for the purposes of the labs. However, if you use Session Manager for other use cases you may need to revert the changes as needed.

<span class="image">![Session Preferences](1-session-prefs.png?raw=true)</span>

Next, navigate to the **Sessions** tab, and click the **Start session** button.

<span class="image">![Start Session](1-start-session.png?raw=true)</span>

Please select the EC2 instance to establish a session with. The workstation is named `labstack-bastion-host`, select it and click **Start session**.

<span class="image">![Conenct Instance](1-connect-session.png?raw=true)</span>


If you see a black command like terminal screen and a prompt, you are now connected to the EC2 based workstation. With Session Manager it is not necessary to allow SSH access to the EC2 instance from a network level, reducing the attack surface of that EC2 instance.

**If you have completed the previous lab**, and created the Aurora DB cluster manually, please execute the following commands to ensure you have a consistent experience compared for subsequent labs. These commands will save the database username and password in environment variables. When the cluster is provisioned automatically by CloudFormation this is done automatically.

```
bash
cd ~
export DBUSER="masteruser"
export DBPASS="<type your password>"
echo "export DBPASS=\"$DBPASS\"" >> /home/ubuntu/.bashrc
echo "export DBUSER=$DBUSER" >> /home/ubuntu/.bashrc
```

**If you have not created the DB cluster manually**, execute the following commands to ensure a consistent experience.

```
bash
cd ~
```


## 2. Connecting to the DB cluster

Connect to the Aurora database just like you would to any other MySQL-based database, using a compatible client tool. In this lab you will be using the `mysql` command line tool to connect. The command is as follows:

```
mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```

If you have completed the previous lab, and created the Aurora DB cluster manually, you would input the **Cluster Endpoint** of that cluster as displayed at the end of that lab.

However, if you have skipped that lab and provisioned the cluster using the CloudFormation template, you can find the value for the cluster endpoint parameter in the stack outputs. We have set the DB cluster's database credentials automatically for you, and have also created the schema named `mylab` as well. The credentials were saved to an <a href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html" target="_blank">AWS SecretsManager</a> secret.

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
--- | --- | --- | --- | ---
-h | [clusterEndpoint] | See CloudFormation stack output | See previous lab | The cluster endpoint of the Aurora DB cluster.
-u | `$DBUSER` | Set automatically, see Secrets Manager | `masteruser` or manually set | The user name of the MySQL user to authenticate as.
-p | `$DBPASS` | Set automatically, see Secrets Manager | Manually set | The password of the MySQL user to authenticate as.
| [database] | `mylab` | `mylab` or manually set | The schema (database) to use by default.

!!! note
    You can view and retrieve the credentials stored in the secret using the following command:

    ```
    aws secretsmanager get-secret-value --secret-id [secretArn] | jq -r '.SecretString'
    ```

Once connected to the database, use the code below to create a stored procedure we'll use later in the labs, to generate load on the DB cluster. Run the following SQL queries:

```
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

Run the load generation script from the Session Manager workstation command line:

```
python3 loadtest.py -e [readerEndpoint] -u $DBUSER -p "$DBPASS" -d mylab
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
--- | --- | --- | --- | ---
-e | [readerEndpoint] | See CloudFormation stack output | See previous lab | The reader endpoint of the Aurora DB cluster.
-u | `$DBUSER` | Set automatically, see Secrets Manager | `masteruser` or manually set | The user name of the MySQL user to authenticate as.
-p | `$DBPASS` | Set automatically, see Secrets Manager | Manually set | The password of the MySQL user to authenticate as.
-d | [database] | `mylab` | `mylab` or manually set | The schema (database) to generate load against.
-t |  | 64 (default) | 64 (default) | The number of client connections (threads) to use concurrently.

Now, open the <a href="https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2#databases:" target="_blank">Amazon RDS service console</a> in a different browser tab.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Take note that the reader node is currently receiving load. It may take a minute or more for the metrics to fully reflect the incoming load.

<span class="image">![Reader Load](4-read-load.png?raw=true)</span>

After several minutes return to the list of instances and notice that a new reader is being provisioned to your cluster.

<span class="image">![Application Auto Scaling Creating Reader](4-aas-create-reader.png?raw=true)</span>

Once the new replica becomes available, note that the load distributes and stabilizes (it may take a few minutes to stabilize).

<span class="image">![Application Auto Scaling Creating Reader](4-read-load-balanced.png?raw=true)</span>

You can now toggle back to the Session Manager command line, and type `CTRL+C` to quit the load generator. After a while the additional reader will be removed automatically.