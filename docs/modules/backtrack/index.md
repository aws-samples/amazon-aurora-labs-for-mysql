# Backtracking a Cluster

::TODO:: Insert overview description here

1.	Reconnect to the cloned cluster using:

    ```
    quit;

    mysql -h [cluster endpoint of clone cluster] -u masteruser -p mylab
    ```

2.	Drop the `sbtest1` table:

    Note: Consider executing the commands below one at a time, waiting a few seconds between each one. This will make it easier to determine a good point in time for testing backtrack.

    ```
    select current_timestamp();

    drop table sbtest1;

    select current_timestamp();

    quit;
    ```

3.	Remember or save the time markers displayed above, you will use them as references later.

4.	Run the following command to replace the dropped table using the sysbench command:

    ```
    sysbench oltp_write_only --threads=1 --mysql-host=[cluster endpoint of clone cluster] --mysql-user=masteruser --mysql-password=Password1 --mysql-port=3306 --tables=1 --mysql-db=mylab --table-size=1000000 prepare
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
