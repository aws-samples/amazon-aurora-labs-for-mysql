# Backtracking a Cluster

This lab will walk you through the process of backtracking a DB cluster. <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Managing.Backtrack.html" target="_blank">
Backtracking</a> "rewinds" the DB cluster to the time you specify. While it is not a replacement for backing up your DB cluster for DR purposes, backtracking allows you to easily undo mistakes quickly, or explore earlier data changes.

This lab contains the following tasks:

1. Making unintended data changes
2. Backtracking to recover from unintended changes

## 1. Making unintended data changes

Connect to the DB cluster endpoint using the MySQL client, if you are not already connected from completing the previous lab:

```
mysql -h [clusterEndpoint] -u [username] -p [database]
```

If you have opted to create the DB cluster using CloudFormation, you can use the following command instead:

```
quit;

mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
--- | --- | --- | --- | ---
-h | [clusterEndpoint] | See CloudFormation stack output | See previous lab | The cluster endpoint of the Aurora DB cluster.
-u | [username] | `$DBUSER` | `masteruser` or manually set | The user name of the MySQL user to authenticate as.
-p | [password] | `$DBPASS` | Manually set, enter when prompted | The password of the MySQL user to authenticate as.
| [database] | `mylab` | `mylab` or manually set | The schema (database) to use by default.

Drop the `sbtest1` table:

!!! note
    Consider executing the commands below one at a time, waiting a few seconds between each one. This will make it easier to determine a good point in time for testing backtrack. In a real world situation, you will not always have a clean marker to determine when the unintended change was made. Thus you might need to backtrack a few times to find the right point in time.

```
SELECT current_timestamp();

DROP TABLE sbtest1;

SELECT current_timestamp();

quit;
```

Remember or save the time markers displayed above, you will use them as references later, to simplify determining the right point in time to backtrack to, for demonstration purposes.

<span class="image">![Drop Table](1-drop-table.png?raw=true)</span>

Now, run the following command to replace the dropped table using the sysbench command, from your EC2-based workstation command line:

```
sysbench oltp_write_only --threads=1 --mysql-host=[clusterEndpoint] --mysql-user=[username] --mysql-password=[password] --mysql-port=3306 --tables=1 --mysql-db=[database] --table-size=1000000 prepare
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
--- | --- | --- | --- | ---
--threads | | 1 | 1 | Number of concurrent threads.
--mysql-host | [clusterEndpoint] | See CloudFormation stack output | See previous labs | The cluster endpoint of the Aurora DB cluster.
--mysql-user | [username] | `$DBUSER` | `masteruser` or manually set | The user name of the MySQL user to authenticate as.
--mysql-password | [password] | `$DBPASS` | Manually set | The password of the MySQL user to authenticate as.
--mysql-port | | 3306 | 3306 | The port the Aurora database engine is listening on.
--tables | | 1 | 1 | Number of tables to create.
--mysql-db | [database] | `mylab` | `mylab` or manually set | The schema (database) to use by default.
--table-size | | 1000000 | 1000000 | The number or rows to generate in the table.

<span class="image">![Sysbench Prepare](1-sysbench-prepare.png?raw=true)</span>

Reconnect to the DB cluster, and run the checksum table operation, the checksum value should be different than the source cluster value calculated in the [Cloning Clusters](/modules/clone/#2-verifying-that-the-data-set-is-identical) lab:

```
mysql -h [clusterEndpoint] -u [username] -p [database]

checksum table sbtest1;

quit;
```

If you have opted to create the DB cluster using CloudFormation, you can use the following command instead:

```
mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab

checksum table sbtest1;

quit;
```

## 2. Backtracking to recover from unintended changes

Backtrack the database to a time slightly after the second time marker. (Right after dropping the table).

!!! note
    Backtrack operations occur at the DB cluster level, the entire database state is rolled back to a designated point in time, even though the example in this lab illustrates the effects of the operation on an individual table.


```
aws rds backtrack-db-cluster --db-cluster-identifier [clusterName] --backtrack-to "yyyy-mm-ddThh:mm:ssZ"
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
--- | --- | --- | --- | ---
--db-cluster-identifier | [clusterName] | `labstack-cluster` | See previous labs | The DB cluster identifier set at cluster creation time
--backtrack-to | yyyy-mm-ddThh:mm:ssZ | See time markers displayed around the drop table operation | See time markers displayed around the drop table operation | The point in time to "rewind" the DB cluster to.

<span class="image">![Backtrack Command](2-backtrack-command.png?raw=true)</span>

Run the below command to track the progress of the backtracking operation. The operation should complete in a few minutes.

```
aws rds describe-db-clusters --db-cluster-identifier [clusterName] | jq -r '.DBClusters[0].Status'
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
--- | --- | --- | --- | ---
--db-cluster-identifier | [clusterName] | `labstack-cluster` | See previous labs | The DB cluster identifier set at cluster creation time

<span class="image">![Backtrack Status](2-backtrack-status.png?raw=true)</span>

::TODO::

Connect back to the database. The `sbtest1` table should be missing from the database.

```
mysql -h [clusterEndpoint] -u [username] -p [database]

show tables;

quit;
```

If you have opted to create the DB cluster using CloudFormation, you can use the following command instead:

```
mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab

show tables;

quit;
```

<span class="image">![Show Tables](2-show-tables.png?raw=true)</span>

Now backtrack again to a time slightly before the first time marker above. (Right before dropping the table).

```
aws rds backtrack-db-cluster --db-cluster-identifier [clusterName] --backtrack-to "yyyy-mm-ddThh:mm:ssZ"
```

Track the progress of the backtracking operation, using the command below. The operation should complete in a few minutes.

```
aws rds describe-db-clusters --db-cluster-identifier [clusterName] | jq -r '.DBClusters[0].Status'
```

Connect back to the database again. The `sbtest1` table should now be available in the database again, but contain the original data set.

```
mysql -h [clusterEndpoint] -u [username] -p [database]

show tables;

checksum table sbtest1;

quit;
```

If you have opted to create the DB cluster using CloudFormation, you can use the following command instead:

```
mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab

show tables;

checksum table sbtest1;

quit;
```
