# Observe and Identify SQL Performance Issues

This lab contains the following tasks:

1. Prepare the initial dataset
2. Verify the slow query log is configured correctly
3. Run a sample workload
4. Monitor database performance using Amazon CloudWatch Metrics
5. Monitor database performance using Amazon RDS Enhanced Monitoring
6. Dive deeper with Performance Insights
7. Download slow query logs
8. Leverage Amazon CloudWatch Logs and Log Insights to view and analyze slow queries
9. Optional: Process slow query logs with Percona's pt-query-digest
10. Summary

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/)
* [Connect to the Session Manager Workstation](/prereqs/connect/)
* [Create a New DB Cluster](/provisioned/create/) (conditional, only if you plan to create a cluster manually)
* [Connect, Load Data](/provisioned/interact/) (connectivity and data loading sections only)


## 1. Prepare the initial dataset

Connect to the Aurora database just like you would to any other MySQL-based database, using a compatible client tool. In this lab you will be using the mysql command line tool to connect. If you are not already connected to the Session Manager workstation command line from previous labs, please connect following these [instructions](https://awsauroralabsmy.com/prereqs/connect/). Once connected, run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster.

```shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```

Once connected to the database, please use the code below to create the schema and stored procedure we'll use later in the lab, to generate load on the DB cluster. Run the following SQL queries:

```sql
DROP TABLE IF EXISTS `weather`;
CREATE TABLE `weather` (
  `date_Str` date NOT NULL COMMENT 'Date and Time of Readings',
  degres_from_mean varchar(100) DEFAULT NULL,
  id varchar(11) NOT NULL COMMENT 'station id',
  longitude decimal(20,4) NOT NULL COMMENT 'longitude',
  latitude decimal(20,4) NOT NULL COMMENT 'latitude',
  max_temp decimal(20,2) NOT NULL COMMENT 'max temp logged',
  min_temp decimal(20,2) NOT NULL COMMENT 'min temp logged',
  station_name char(50) NOT NULL COMMENT 'station names',
  type char(25) NOT NULL COMMENT 'weather condition',
  serialid int(11) NOT NULL COMMENT 'serial id of log'
) ENGINE=InnoDB DEFAULT CHARSET=latin1 ;
```

```sql
DELIMITER $$
DROP PROCEDURE IF EXISTS insert_temp;
CREATE PROCEDURE insert_temp()
BEGIN
DECLARE key_value,key_value1,key_value2 int;
set key_value =FLOOR(3196831 + RAND() * 3200000);
INSERT INTO mylab.weather VALUES (1993-12-10,14.38,'USC00147271',-100.92,38.47,21.70,-4.40,'SCOTT CITY','Weak Hot',key_value);
DELETE from mylab.weather  where serialid=key_value;
END$$
DELIMITER ;
```

Next, load an initial data set by importing data from an Amazon S3 bucket:

```sql
LOAD DATA FROM S3 's3-us-east-1://awsauroralabsmy-us-east-1/samples/weather/anomalies.csv'
INTO TABLE weather CHARACTER SET 'latin1' fields terminated by ',' OPTIONALLY ENCLOSED BY '\"' ignore 1 lines;
```

Data loading may take several minutes, you will receive a successful query message once it completes.

## 2. Verify the slow query log is configured correctly

In many cases the slow query log can be used to find queries that take a long time to execute and are therefore candidates for optimization. Slow query logs are controlled by various parameters and the most notable ones are **[slow_query_log](https://dev.mysql.com/doc/refman/5.7/en/server-system-variables.html#sysvar_slow_query_log), [long_query_time](https://dev.mysql.com/doc/refman/5.7/en/server-system-variables.html#sysvar_long_query_time) and [log_output](https://dev.mysql.com/doc/refman/5.7/en/server-system-variables.html#sysvar_log_output)** .

!!! error "Lab change"
    I changed the instruction below, because according to the lab flow, you were still connected to the mysql client after the previous command, so using the old command would have resulted in an error because you were not on the linux shell.

While still connected to the database, run the query below:

```sql
SELECT @@slow_query_log,@@long_query_time,@@log_output;
```

<span class="image">![long query output](long_query_out.png?raw=true)</span>

??? tip  "Changing slow query log settings in production"
    In production systems, you can change the values for **long_query_time** in multiple iterations eg. 10 to 5 and then 5 to 3 and so on.

Before proceeding further, please ensure the output looks like above. When completed, exit the MySQL command line:

```shell
quit;
```

??? tip "Other useful parameters related to slow_log"
    There are other useful parameters like [log_queries_not_using_indexes](https://dev.mysql.com/doc/refman/5.7/en/server-system-variables.html#sysvar_log_queries_not_using_indexes), [log_slow_admin_statements](https://dev.mysql.com/doc/refman/5.7/en/server-system-variables.html#sysvar_log_slow_admin_statements).

## 3. Run a sample workload

Next, please run the following command to generate a workload, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster.

```shell
python3 weather_perf.py -e[clusterEndpoint] -u$DBUSER -p"$DBPASS" -dmylab
```
This script will take about **4~5** minutes to complete.

## 4. Monitor database performance using Amazon CloudWatch Metrics

To monitor DB instances you can use Amazon CloudWatch, which collects and processes raw data from Amazon RDS into readable, near real-time metrics. Open the [Amazon RDS service console](https://console.aws.amazon.com/rds/home) and click on [Databases](https://console.aws.amazon.com/rds/home#databases:) from left navigation pane. From list of databases click on auroralab-mysql-node-1 under *DB identifier*. On the database details view, click on the *Monitoring* tab and pick CloudWatch metrics from Monitoring.

Although all the metrics are important to monitor, the base metrics like *CPU, DB connections, write latency,* *Read latency* etc are spiking up during this workload. You can click on a chart to drill down for more details, select any chart area to zoom in on a specific time period to understand the overall workload and its impact on the database.

<span class="image">![CloudWatch Metrics](db-cpu.png?raw=true)</span>

<span class="image">![CloudWatch Metrics](latency.png?raw=true)</span>

Amazon Aurora also provides a range of dedicated [CloudWatch metrics](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraMySQL.Monitoring.Metrics.html) populated with various database status variables. This example shows how to interpret *DML metrics (*using the search bar*)* for this period.

In general,

* Database activity variables responsible for tracking *throughput* are modified when the statement is received by the server.
* Database activity variables responsible for tracking *latency* are modified after the statement completes. This is quite intuitive: statement latency (i.e. execution time) is not known until the statement finishes.

<span class="image">![CloudWatch Metrics](DML_throughput.png?raw=true)</span> <span class="image">![CloudWatch Metrics](DML_latency.png?raw=true)</span>

??? tip "Learn more about Aurora monitoring"
    To learn more about how to plan for Aurora monitoring and performance guidelines please refer our [Aurora Monitoring documentation](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/MonitoringOverview.html).

DMLLatency metric reveals a spike at 22:57, when the metric reached 4442 milliseconds. In other words, 4.4 seconds is the average latency of all DML statements that finished during this 1-minute period. 4 seconds is significantly higher than the baseline latency observed before the spike, therefore it’s worth investigating.

A useful piece of information readily available from DMLThroughput metric . At 22.57 DML throughput is 0.907 which is roughly 54 operations. This could be the reason for the DML latency we noticed before.

```shell
.907 Operations
     ---------- X 60s= 54.42 ~ 54 operations
        s
```

!!! note "Monitoring the baseline"
    Once the performance baseline is understood you can setup alarms against CloudWatch metrics when it exceeds the baseline for corrective actions.

## 5. Monitor database performance using Amazon RDS Enhanced Monitoring

You must have noticed that the CloudWatch metrics didn’t start populating right away as it takes 60 seconds interval period to capture data points. However to monitor and understand OS/host level metrics eg. if the CPU is consumed by user or system, free/active memory for as granular as 1 second interval, [Enhanced Monitoring (EM)](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.CloudWatchLogs.html) should help.

If you have Enhanced Monitoring option enabled for the database instance, you can view the metrics by selecting the **node(writer)** -> **Monitoring** -> select **Enhanced Monitoring** option from the Monitoring **dropdown** list. For more information about enabling and using the Enhanced Monitoring feature, please refer to the [Enhanced Monitoring doc](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_Monitoring.OS.html).

<span class="image">![EM](EM.png?raw=true)</span>

From the above, you can see when the workload kicked in, there is a sharp *spike* in CPU driven by *User* and *drop* in Free memory. You can also see the *Load average* of the DB instance increased during this period.

!!! tip "Additional metrics available"
    You will see additional counters showing metrics captured at the guest OS level as well as local, temporary storage (not the Aurora storage volume).

## 6. Dive deeper with Performance Insights

Amazon RDS Performance Insights monitors your Amazon RDS DB instance load so that you can analyze and troubleshoot your database performance. To view the current performance insights dashboard, please go to the [RDS console](https://console.aws.amazon.com/rds/) and in the navigation pane, click performance insights and choose the writer node. You should see the console like below.  

<span class="image">![Performance Insights](P.I_load.png?raw=true)</span>

The dashboard is divided into 3 sections(Counter Metrics, Database Load and Top SQL activity), allowing you to drill down from high level performance indicator metrics down to individual *queries*, *wait events*, *latency* etc. You can learn more about this in the [Performance Insights lab](https://awsauroralabsmy.com/provisioned/perf-insights/).

**Add additional counters:**

Let’s start by adding counters in the *Counter Metrics* under Manage Metrics. This collects metrics from *DB* like innodb_rows_read, threads_running etc and *OS* metrics like cpuUtilization total, user etc which adds valuable information on top of CloudWatch metrics.

<span class="image">![Performance Insights](counter_manage.png?raw=true)</span>

Enable `slow_queries` under **Database metrics** and `cpuUtilization` - `total` under **OS metrics**.

<span class="image">![Performance Insights](P.I_counter_split.png?raw=true)</span>

Click **Update graph** and once done, the counter metrics should look like below. You can see the CPU spike of ~100% for the ~4 minute period and the number of rows read is `1+ million` and slow logs were getting logged for this duration.

<span class="image">![Performance Insights](counter_before_index.png?raw=true)</span>

**Get a different perspective of Database Load:**

Let's look at the DB wait events to understand the workload. You can see different wait events on the right hand side. Amazon Aurora MySQL specific **wait events** are documented in the [Amazon Aurora MySQL Reference guide](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Reference.html#AuroraMySQL.Reference.Waitevents).

<span class="image">![Performance_schema_Load](P.I_DB_Load_1.png?raw=true)</span>

You can also change the view of **DB Load** section from `Slice by wait` to `Slice by SQL` to understand the AAS of different queries during this time. You can also see the the max number of available **vCPUs** is 2 but the current sessions exceeds the max vCPU and this in many cases would be driving factor for CPU/memory consumption.

<span class="image">![Performance_schema_Load2](P.I_DB_Load_2.png?raw=true)</span>

**Review additional information from the session activity:**

Now let’s modify the **Session activity** section. The default interface for `Top SQL` contains AAS and SQL statements should look like this. Please go to **Preferences** (gear icon at the right hand bottom) and add additional columns.

<span class="image">![SQL troubleshooting](session_manage.png?raw=true)</span>

To understand the performance profile it’s important to have additional information about the query access pattern. For the purpose of this lab, please enable `Rows affected/sec`, `Rows affected/call`, `Rows examined/sec`, `Rows examined/call`, `Rows sent/sec`, `Rows sent/call` and click **Save**.

<span class="image">![P.I](P.I_expand_gear.png?raw=true)</span>

Once saved, the session activity for **Top SQL** would look like below. You should be able to see **rows examined/s** vs **rows sent/s** and corresponding **avg. latency** in ms/call. You should focus on the queries with large difference between rows examined and rows sent.

<span class="image">![SQL troubleshooting](P.I_expand.png?raw=true)</span>

!!! tip "What's inside a stored procedure"
  To see the queries inside a stored procedure, please click and expand the `+` (plus) icon.

You can note down the top SQL queries but please keep in mind not all **Top SQL** queries are slow queries it only means that these queries are consuming the load at given point of time.

You can use Performance Insights to understand average activity, however to get individual query statistics and execution time, you should leverage the slow query log.

## 7. Download slow query logs

In this sections you will learn how to view the slow query logs using the AWS Management Console. Since the workload script was ran against the cluster endpoint (which points to the writer node by default), you should check the writer node logs. You can open the Amazon [RDS service console](https://console.aws.amazon.com/rds/home#database:id=auroralab-mysql-cluster;is-cluster=true;tab=monitoring) and click the cluster and select the writer node. Once selected, under **Logs & Events** please scroll down to the **Logs** section.

<span class="image">![SQL troubleshooting](console_slow_view.png?raw=true)</span>

You can select the slow query log for the timeframe and **view** or **watch** it. Below example shows the log when you **view** it.

<span class="image">![SQL troubleshooting](console_opt_view.png?raw=true)</span>

You should see slow queries in the console. The log file content will have the following

* `Query_time`: The statement execution time in seconds.
* `Lock_time`: The time to acquire locks in seconds.
* `Rows_sent`: The number of rows sent to the client.
* `Rows_examined`: The number of rows examined by the server layer (not counting any processing internal to storage engines).

To learn more about slow queries, please check the [MySQL documentation](https://dev.mysql.com/doc/refman/5.7/en/slow-query-log.html).

You can download the logs via the AWS Management Console or the AWS CLI using the [download-db-log-file-portion](https://docs.aws.amazon.com/cli/latest/reference/rds/download-db-log-file-portion.html) API call. For now, we'll call this log as `slow_query_log1`.

!!! note "Log rotation"
    Log gets rotated hourly so please ensure the logs are downloaded for the correct workload period.

## 8. Leverage Amazon CloudWatch Logs and Log Insights to view and analyze slow queries

Slow logs are great for troubleshooting, but viewing or downloading individual logs could be time consuming. Also, logs could get rotated periodically. In addition to viewing and downloading DB instance logs from the console, you can **publish** logs to Amazon CloudWatch Logs. With CloudWatch Logs, you can perform real-time analysis of the log data, store and retain the data in highly durable storage, and manage the data with the CloudWatch Logs Agent.


!!! error "Lab issue"
    We have students enable log publication even if they create the cluster manually in the Create DB Cluster lab. Might be worth removing the "if the cluster was created automatically... if not..." part and just say that the clsuter should already have log publication enabled, but they can verify that by checking the console.

If the DB cluster was created automatically, you can see that the export CloudWatch logs option is already enabled.
This can be verified by going to the RDS console, under cluster **Configuration** → **Published logs** like below. Please proceed to next step only if you see slow query in it. However if you are creating the cluster manually please make sure you enable this option by modifying the database instance using RDS console before proceeding further.

<span class="image">![CloudWatchL](CWL1.png?raw=true)</span>

!!! note "Enabling log export"
    To enable/disable these logs or add additional logs, you can click **Modify** on the top right of the panel → **Log exports** → check/uncheck preferred logs → **Continue** → **Modify cluster**.

<span class="image">![CloudWatchL](CwL2.png?raw=true)</span>

**View exported logs in CloudWatch**

Once you have verified that log exports are configured correctly, you can access the logs in CloudWatch Logs. A new log group is automatically created for the Aurora DB cluster under the following prefix, in which ==[cluster-name]== represents the DB cluster name, and ==[log_type]== represents the log type.

```shell
/aws/rds/cluster/[cluster-name]/[log_type]
```

For our DB cluster `auroralab-mysql-cluster`, slow query data is stored in the `/aws/rds/cluster/auroralab-mysql-cluster/slowquery` log group. Open the [Amazon CloudWatch](https://console.aws.amazon.com/cloudwatch/home?p=clw&cp=bn&ad=c) console and select **Log groups** on the left hand side and search for auroralab-mysql-cluster/slowquery and it should see like below

<span class="image">![CloudWatchL](CWL_slow_query_1.png?raw=true)</span>

Under **Log streams**, pick your current **writer** node (since that is where the script was ran against) to view the slow query logs and you should see like below:

<span class="image">![CloudWatchL](CWL_slow_query_select.png?raw=true)</span>

!!! tip "Log retention"
  The default log retention period is `Never Expire`, however this can be changed. Please see [Change log data retention in CloudWatch Logs](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/SettingLogRetention.html) in the documentation.

To increase the readability of these logs, you are going to use [Amazon CloudWatch Insights](https://console.aws.amazon.com/rds/home#database:id=auroralab-mysql-cluster;is-cluster=true;tab=logs-and-events). Click on the **Insights** option in the sidebar menu and select your log group in the drop down list. For slow queries, it will be in the format of `/aws/rds/cluster/auroralab-mysql-cluster/slowquery`. In the text field, enter the following insights query by replacing the ==[writerNode]== placeholder with the database instance ID (name) of your active writer node in the cluster:

```shell
filter @logStream = '[writerNode]'
| parse @message "# Time: * User@Host: * Id: * Query_time: * Lock_time: * Rows_sent: * Rows_examined: * timestamp=*;*" as Time, User, Id, Query_time, Lock_time, Rows_sent, Rows_examined, Timestamp, Query
| display Time, Query_time, Query, Rows_sent, Rows_examined
| sort Query_time asc
```

This query parses the slow query logs and captures the individual fields like `Time`, `Query_time`, `Query`, `Rows_sent`, `Rows_examined`. Once entered click **Run query**, the output should look similar to the screenshot below.

<span class="image">![CloudWatchL](CWL_slow_query.png?raw=true)</span>

Only the sueries that take longer than the parameter value of `long_query_time` (see above) will be listed. You can see there are around 100+ entries in the last 30 minutes. You can select any query to expand to find more information about it.

<span class="image">![CloudWatchL](CWL_slow_query_expand.png?raw=true)</span>

You can also export the results to a CSV-formatted file for easier analysis. For now call it as `slow_query_log2`.

## 9. Optional: Process slow query logs with Percona's pt-query-digest

Normally, some amount of manual or automation effort is needed to find unique patterns/queries from the slow query logs and such work scales poorly when you are operating many databases. In order to find the unique queries, there are several third party tools that can help, and one of them is **pt-query-digest**, part of the Percona Toolkit.

!!! note "Disclaimer"
    Percona pt-query-digest is a third party software licensed under GNU so please use [official documentation](https://www.percona.com/doc/percona-toolkit/2.0/pt-query-digest.html) for reference.

**pt-query-digest** analyzes MySQL queries from slow, general, and binary log files. It summaries the top queries based on the input log file, ranked by response time. To save time and complexity, we have already installed this tool in your lab environment. You can learn more and find installation instructions on the [Percona Toolkit](https://www.percona.com/doc/percona-toolkit/LATEST/installation.html) website.

First, you need to download the **slow query logs** from the database instance. You can either do this using the RDS Console, or the AWS CLI.

!!! error "Lab issue"
    Since the pt-query-digest command will be run on the EC2 workstation, there's no point in showing them how to download it via the RDS console, because if students do it that way, they end up with a file on their own computers that they then either need to upload to the EC2 workstation (complicated) or need to install Percona toolkit locally (complicated/error prone). Suggest you only show and use the CLI command.

=== "Download using RDS Console"
    <span class="image">![PTQ](view_slow_logs.png?raw=true)</span>

    Please note that logs get rotated hourly, please ensure you are downloading the logs for the workload period of time.

=== "Download using the AWS CLI"
    ```shell
    aws rds download-db-log-file-portion --db-instance-identifier [writerendpoint] \
    --starting-token 0 --output text --log-file-name slowquery/<slowlogname> > slow_log_file.txt
    ```

Once downloaded, you can run the pt-query-digest like below using the slow query log file you have just downloaded. Please ensure the log file name is correct, based on the file you .

```shell
$ pt-query-digest <slow_log_file.txt>
```

(1) This is a highly summarized view of the unique events in the detailed query report that follows. It contains the following columns and basically ranks the top slow running queries and rank them for readability:

```shell
Column        Meaning
============  ==========================================================
Rank          The query's rank within the entire set of queries analyzedQuery ID      The query's fingerprint
Response time The total response time, and percentage of overall total
Calls         The number of times this query was executed
R/Call        The mean response time per execution
V/M           The Variance-to-mean ratio of response time
Item          The distilled query
```

<span class="image">![PTQ](PTQ2.png?raw=true)</span>

For the queries listed above in the previous section, this section contains individual metrics about each query ID with stats like `concurrency` (calculated as a function of the timespan and total `Query_time`), `exec time`, `rows sent`, `rows examine` etc. This also provides the number of occurrences of a query in the slow log. You can collect these slow logs in a file and call them as `slow_query_log3`.

<span class="image">![PTQ](PTQ3.png?raw=true)</span>

## 10. Summary

In this exercise you have use

*  RDS monitoring tools like CloudWatch Metrics, Enhanced Monitoring to understand the database workload.
*  RDS performance monitoring tools like Performance Insights and its counters to understand the workload.
*  MySQL slow query logs using RDS console, AWS CLI, CloudWatch logs, log insights and Percona pt-query-digest to understand the pattern of  queries.

If you are interested in learning what to do with the captured slow query logs, please proceed to the next lab: [Analyze SQL Query Performance](/provisioned/perf-analysis/).
