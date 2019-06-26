# Backtracking a Cluster

::TODO:: Insert overview description here

1.	Connect to the DB cluster endpoint using the MySQL client, if you are not already connected from completing the previous lab:

    ```
    mysql -h [clusterEndpoint] -u [username] -p [password] [database]
    ```

    **Command parameter values at a glance:**

    Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
    --- | --- | --- | --- | ---
    -h | [clusterEndpoint] | See CloudFormation stack output | See previous lab | The cluster endpoint of the Aurora DB cluster.
    -u | [username] | `$DBUSER` | `masteruser` or manually set | The user name of the MySQL user to authenticate as.
    -p | [password] | `$DBPASS` | Manually set | The password of the MySQL user to authenticate as.
    | [database] | `mylab` | `mylab` or manually set | The schema (database) to use by default.

2.	Drop the `sbtest1` table:

    Note: Consider executing the commands below one at a time, waiting a few seconds between each one. This will make it easier to determine a good point in time for testing backtrack.

    ```
    SELECT current_timestamp();

    DROP TABLE sbtest1;

    SELECT current_timestamp();

    quit;
    ```

    Remember or save the time markers displayed above, you will use them as references later, to simplify determining the right point in time to backtrack to, for demonstration purposes.

3.	Run the following command to replace the dropped table using the sysbench command, from your EC2-based workstation command line:

    ```
    sysbench oltp_write_only --threads=1 --mysql-host=[cluster endpoint of clone cluster] --mysql-user=[username] --mysql-password=[password] --mysql-port=3306 --tables=1 --mysql-db=[database] --table-size=1000000 prepare
    ```

5.	Reconnect to the cloned cluster, and checksum the table again, the checksum value should be different than both the original clone value and source cluster:

    ```
    mysql -h [cluster endpoint of clone cluster] -u masteruser -p mylab

    checksum table sbtest1;

    quit;
    ```

6.	Backtrack the database to a time slightly after the second time marker. (Right after dropping the table).

    ```
    aws rds backtrack-db-cluster --db-cluster-identifier [clusterName]-clone --backtrack-to "yyyy-mm-ddThh:mm:ssZ"
    ```

7.	Run the below command to track the progress of the backtracking operation. The operation should complete in a few minutes.

    ```
    aws rds describe-db-clusters --db-cluster-identifier [clusterName]-clone | grep -i EngineMode -A 2 | grep Status
    ```

8.	Connect back to the database. The `sbtest1` table should be missing from the database.

    ```
    mysql -h [cluster endpoint of clone cluster] -u masteruser -p mylab

    show tables;

    quit;
    ```

9.	Now backtrack again to a time slightly before the first time marker above. (Right before dropping the table).

    ```
    aws rds backtrack-db-cluster --db-cluster-identifier [clusterName]-clone --backtrack-to "yyyy-mm-ddThh:mm:ssZ"
    ```

10.	Run the below command to track the progress of the backtracking operation. The operation should complete in a few minutes.

    ```
    aws rds describe-db-clusters --db-cluster-identifier [clusterName]-clone | grep -i EngineMode -A 2 | grep Status
    ```

11.	Connect back to the database. The `sbtest1` table should now be available in the database again, but contain the original data set.

    ```
    mysql -h [cluster endpoint of clone cluster] -u masteruser -p mylab

    show tables;

    quit;
    ```
