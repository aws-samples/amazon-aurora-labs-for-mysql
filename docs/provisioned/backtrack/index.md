# Backtrack a DB Cluster

This lab will walk you through the process of backtracking a DB cluster. <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Managing.Backtrack.html" target="_blank">
Backtracking</a> "rewinds" the DB cluster to the time you specify. While it is not a replacement for backing up your DB cluster for DR purposes, backtracking allows you to easily undo mistakes quickly, or explore earlier data changes.

This lab contains the following tasks:

1. Make unintended data changes
2. Backtrack to recover from unintended changes

This lab requires the following prerequisites:

* [Deploy Environment](/prereqs/environment/)
* [Connect to the Session Manager Workstation](/prereqs/connect/)
* [Create a New DB Cluster](/provisioned/create/) (conditional, only if you plan to create a cluster manually)
* [Connect, Load Data and Auto Scale](/provisioned/interact/) (connectivity and data loading sections only)


## 1. Make unintended data changes

If you are not already connected to the Session Manager workstation command line, please connect [following these instructions](/prereqs/connect/). Then, connect to the DB cluster endpoint using the MySQL client, if you are not already connected after completing the previous lab, by running:

```
mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```

Next, drop the `sbtest1` table:

!!! note
    Consider executing the commands below one at a time, waiting a few seconds between each one. This will make it easier to determine a good point in time for testing backtrack. In a real world situation, you will not always have a clean marker to determine when the unintended change was made. Thus you might need to backtrack a few times to find the right point in time.

```
SELECT current_timestamp();

DROP TABLE sbtest1;

SELECT current_timestamp();

quit;
```

Remember or save the time markers displayed by the commands above, you will use them as references later, to simplify determining the right point in time to backtrack to for demonstration purposes.

<span class="image">![Drop Table](1-drop-table.png?raw=true)</span>

Now, run the following command to replace the dropped table using the sysbench command, replacing the ==[clusterEndpont]== placeholder with the cluster endpoint of your DB cluster:

```
sysbench oltp_write_only \
--threads=1 \
--mysql-host=[clusterEndpoint] \
--mysql-user=$DBUSER \
--mysql-password="$DBPASS" \
--mysql-port=3306 \
--tables=1 \
--mysql-db=mylab \
--table-size=1000000 prepare
```

??? tip "What do all these parameters mean?"
    Parameter | Description
    --- | ---
    --threads | Number of concurrent threads.
    --mysql-host | The cluster endpoint of the Aurora DB cluster.
    --mysql-user | The user name of the MySQL user to authenticate as.
    --mysql-password | The password of the MySQL user to authenticate as.
    --mysql-port | The port the Aurora database engine is listening on.
    --tables | Number of tables to create.
    --mysql-db | The schema (database) to use by default.
    --table-size | The number or rows to generate in the table.

<span class="image">![Sysbench Prepare](1-sysbench-prepare.png?raw=true)</span>

Reconnect to the DB cluster, and run the checksum table operation, the checksum value should be different than the source cluster value calculated in the [Clone a DB Cluster](/provisioned/clone/#2-verifying-that-the-data-set-is-identical) lab:

```
mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab

checksum table sbtest1;

quit;
```

## 2. Backtrack to recover from unintended changes

Backtrack the database to a time slightly after the second time marker (right after dropping the table).

!!! note
    Backtrack operations occur at the DB cluster level, the entire database state is rolled back to a designated point in time, even though the example in this lab illustrates the effects of the operation on an individual table.

```
aws rds backtrack-db-cluster \
--db-cluster-identifier labstack-cluster \
--backtrack-to "yyyy-mm-ddThh:mm:ssZ"
```

<span class="image">![Backtrack Command](2-backtrack-command.png?raw=true)</span>

Run the below command to track the progress of the backtracking operation. Repeat the command several times, if needed. The operation should complete in a few minutes.

```
aws rds describe-db-clusters \
--db-cluster-identifier labstack-cluster \
| jq -r '.DBClusters[0].Status'
```

<span class="image">![Backtrack Status](2-backtrack-status.png?raw=true)</span>

Connect back to the database. The `sbtest1` table should be missing from the database.

```
mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab

show tables;

quit;
```

<span class="image">![Show Tables](2-show-tables.png?raw=true)</span>

Now backtrack again to a time slightly before the first time marker above (right before dropping the table).

```
aws rds backtrack-db-cluster \
--db-cluster-identifier labstack-cluster \
--backtrack-to "yyyy-mm-ddThh:mm:ssZ"
```

Track the progress of the backtracking operation, using the command below. The operation should complete in a few minutes. Repeat the command several times, if needed.

```
aws rds describe-db-clusters \
--db-cluster-identifier labstack-cluster \
| jq -r '.DBClusters[0].Status'
```

Connect back to the database again. The `sbtest1` table should now be available in the database again, but contain the original data set.

```
mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab

show tables;

checksum table sbtest1;

quit;
```
