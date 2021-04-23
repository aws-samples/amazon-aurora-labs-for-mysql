# Connect, Load Data and Auto Scale

This lab will walk you through the process of connecting to the DB cluster you have just created, and using the cluster for the first time. At the end you will test out how Aurora read replica auto scaling works in practice using a load generator script.

This lab contains the following tasks:

1. Connect to the DB cluster
2. Load an initial data set from S3
3. Run a read-only workload

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/)
* [Connect to the Session Manager Workstation](/prereqs/connect/)
* [Create a New DB Cluster](/provisioned/create/) (conditional, only if you plan to create a cluster manually)


## 1. Connect to the DB cluster

Connect to the Aurora database just like you would to any other MySQL-based database, using a compatible client tool. In this lab you will be using the `mysql` command line tool to connect.

If you are not already connected to the Session Manager workstation command line from previous labs, please connect [following these instructions](/prereqs/connect/). Once connected, run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster.

!!! tip "Where do I find the cluster endpoint (or any other placeholder parameters)?"
    If you have completed the previous lab, and created the Aurora DB cluster manually, you would find the value of the cluster endpoint on the DB cluster details page in the RDS console, as noted at Step 2. in that lab.

    If you are participating in a formal workshop, and the lab environment was provisioned for you using Event Engine, the value of the cluster endpoint may be found on the Team Dashboard in Event Engine.

    Otherwise, you can retrieve the cluster endpoint from the CloudFormation stack **Outputs** as indicated in the [Get Started](/prereqs/environment/) prerequisites module.

```shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```

??? tip "What do all these parameters mean?"
    If you opted to have the DB cluster be created automatically for you using the appropriate CloudFormation template, we have set the DB cluster's database credentials automatically for you. We have also created the schema named `mylab` as well. The credentials were saved to an <a href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html" target="_blank">AWS SecretsManager</a> secret.

    You can view and retrieve the credentials stored in the secret using the following command:

    ```shell
    aws secretsmanager get-secret-value --secret-id [secretArn] | jq -r '.SecretString'
    ```

Once connected to the database, use the code below to create a stored procedure we'll use later in the lab, to generate load on the DB cluster. Run the following SQL queries:

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


## 2. Load an initial data set from S3

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


## 3. Run a read-only workload

Once the data load completes successfully, you can run a read-only workload to generate load on the cluster. You will also observe the effects on the DB cluster topology. For this step you will use the **Reader Endpoint** of the cluster. If you created the cluster manually, you can find the endpoint value as indicated in that lab. If the DB cluster was created automatically for you the value can be found in your CloudFormation stack outputs.

Run the load generation script from the Session Manager workstation command line, replacing the ==[readerEndpoint]== placeholder with the reader endpoint:

```shell
python3 reader_loadtest.py -e[readerEndpoint] -u$DBUSER -p"$DBPASS" -dmylab
```

Now, open the <a href="https://console.aws.amazon.com/rds/home#databases:" target="_blank">Amazon RDS service console</a> in a different browser tab.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Take note that the reader node is currently receiving load. It may take a minute or more for the metrics to fully reflect the incoming load.

<span class="image">![Reader Load](3-read-load.png?raw=true)</span>

After several minutes return to the list of instances and notice that a new reader is being provisioned to your cluster.

<span class="image">![Application Auto Scaling Creating Reader](3-aas-create-reader.png?raw=true)</span>

Once the new replica becomes available, note that the load distributes and stabilizes (it may take a few minutes to stabilize).

<span class="image">![Application Auto Scaling Creating Reader](3-read-load-balanced.png?raw=true)</span>

You can now toggle back to the Session Manager command line, and type `CTRL+C` to quit the load generator. After a while the additional reader will be removed automatically.
