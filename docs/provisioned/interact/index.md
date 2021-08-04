# Connect to the DB Cluster and Load Data

This lab will walk you through the process of connecting to the DB cluster you have just created, and using the cluster for the first time. You will also load an initial data set from Amazon S3.

This lab contains the following tasks:

1. Connect to the DB cluster
2. Load an initial data set from S3

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/)
* [Connect to the Cloud9 Desktop](/prereqs/connect/)
* [Create a New DB Cluster](/provisioned/create/) (conditional, only if you plan to create a cluster manually)


## 1. Connect to the DB cluster

Connect to the Aurora database just like you would to any other MySQL-based database, using a compatible client tool. In this lab you will be using the `mysql` command line tool to connect.

If you have not already opened a terminal window or the Cloud9 desktop in a previous lab, please [following these instructions](/prereqs/connect/) to do so now. Once connected, run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster.

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

Once connected to the database, use the code below to create a stored procedure we'll use in future labs, to generate load on the DB cluster. Run the following SQL queries:

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

Next, load an initial data set by importing data from an object located in an Amazon S3 bucket:

```sql
LOAD DATA FROM S3 MANIFEST
's3-us-east-1://awsauroralabsmy-us-east-1/samples/sbdata/sample.manifest'
REPLACE
INTO TABLE sbtest1
CHARACTER SET 'latin1'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n';
```

Data loading may take several minutes, you will receive a successful query message once it completes.

<span class="image">![Cloud9 MySQL Commands](c9-mysql-commands.png?raw=true)</span>

When completed, exit the MySQL command line:

```sql
quit;
```

You have now completed a few basic commands to interact with your Aurora DB cluster for the first time. These commands illustrate how to:

* create a stored procedure in Aurora MySQL
* create a new table using standard SQL synthax
* load data from files located in an Amazon S3 bucket
