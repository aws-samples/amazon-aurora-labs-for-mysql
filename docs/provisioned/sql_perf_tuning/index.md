Aurora MySQL SQL Performance Troubleshooting (WIP) 

In this lab, we are going to demonstrate *how to troubleshoot SQL performance related issues using* different tools. Specifically we are going to look at how you can leverage *CW metrics, EM metrics*, *P.I, slow query logs, CloudWatch logs and CloudWatch log insights.pt-query-digest ,EXPLAIN, PROFILE*  to troubleshoot / identify bottlenecks. Also we are going to briefly shows how indexes can help in improving the performance of your query.

This lab contains the following tasks:

* *Setup* the environment to capture slow queries
* *Monitor* using *CW* Metrics and Enhanced Monitoring(*EM*)
* *Identify top* queries using performance insights(*P.I*)
* *View* slow queries using  various options like *RDS console, CloudWatch logs, CloudWatch log insights, pt-query digest*
* *Analyse* the slow queries using MySQL *Explain* plan, *profiling*
* *Tune* the Queries
* *Review*

*Optional:* Performance schema

## 1 [Lab setup / Preparation of lab]
  
### Connect to the DB cluster

Connect to the Aurora database just like you would to any other MySQL-based database, using a compatible client tool. In this lab you will be using the mysql command line tool to connect.
If you are not already connected to the Session Manager workstation command line from previous labs, please connect following these [instructions](https://awsauroralabsmy.com/prereqs/connect/). Once connected, run the command below, replacing the [clusterEndpoint] placeholder with the cluster endpoint of your DB cluster.

```shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```
Once connected to the database, use the code below to create the schema and stored procedure we'll use later in the lab, to generate load on the DB cluster. Run the following SQL queries:

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

Load an initial data set from S3

Next, load an initial data set by importing data from an Amazon S3 bucket:

```sql
LOAD DATA FROM S3 's3-eu-west-1://auroralab-data-4cc625f0/weather-anomalies.csv'
INTO TABLE weather CHARACTER SET 'latin1' fields terminated by ',' OPTIONALLY ENCLOSED BY '\"' ignore 1 lines;
```

Data loading may take several minutes, you will receive a successful query message once it completes. When completed, exit the MySQL command line:

```shell
quit;
```

Alternate option to install/load can be found at the bottom of the page https://quip-amazon.com/JdhRAhCPt9Y4 

### Setup Parameters to log slow queries

The slow query log can be used to find queries that take a long time to execute and are therefore candidates for optimization.Slow query logs are controlled by various parameters and the most notable ones are slow_query_log, long_query_time and log_output . MySQL enables you to log queries that exceed a predefined time limit controlled by long_query_time. This greatly simplifies the task of finding inefficient or time-consuming queries.Slow query log (slow_query_log) is *disabled* by default on RDS instances. 

Current setup should look like this when you run the query

```shell
$ mysql -h [cluster endpoint]-u$DBUSER -p"$DBPASS" -e"select @@slow_query_log,@@long_query_time,@@log_output;"
```

[Image: Screenshot 2021-05-06 at 13.26.11.png]
Let’s modify *long_query_time * to 1 second, *slow_query_log to 1*, log_output to *FILE* . To do so, open the [Amazon RDS service console](https://console.aws.amazon.com/rds/home#database:id=auroralab-mysql-cluster;is-cluster=true;tab=monitoring), select the DB instance in the cluster that has the *Writer* role and click on the configuration tab to view the associated DB *Parameter group*.
[Image: Screenshot 2021-04-30 at 00.16.06.png]
*Note:* You can't change values in a default parameter group.To learn more about how to work with custom parameter group please refer to our [doc](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithParamGroups.html#USER_WorkingWithParamGroups.Associating).

Click the *parameter group* associated, which would bring the parameter group page. For *Parameter group actions*, choose *Edit parameters*. Search for long_query_time under parameters and modify the long_query_time  from *10 to 1.*Choose Save changes*. Since long_query_time is a dynamic parameter, no reboot is required. Please wait for the parameter group to sync with DB instance before the slow queries start appearing in the slow query logs.*

<span class="image">![Create Database](1-create.png?raw=true)</span>

[Image: Screenshot 2021-05-01 at 16.52.41.png]

*Hint:* In production systems, you can change the values in multiple iterations eg. 10 to 5 and then 5 to 3 and so on.  

 Now run the command below replacing the [clusterEndpoint] placeholder with the value of the cluster endpoint created in the preceding steps. 

```shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" -e"select @@slow_query_log,@@long_query_time,@@log_output;"
```

Before proceeding further, please ensure the output looks like this.
[Image: Screenshot 2021-05-01 at 17.06.27.png]*Optional:* Please read about log_queries_not_using_indexes ,log_slow_admin_statements 

### Run the workload

On the [session manager terminal](https://awsauroralabsmy.com/prereqs/connect/), please run the following to generate workload.

 Script can be downloaded from https://quip-amazon.com/JdhRAhCPt9Y4

```shell
python3 weather_perf.py -e[clusterendpoint] -u$DBUSER -p"$DBPASS" -dmylab
```
This script will take around **4** minutes to complete.

## 2 Monitor DB performance states using *CloudWatch* Metrics, Enhanced Monitoring(*EM*) and Performance Insights(P.I)

### CloudWatch Metrics

You can monitor DB instances using Amazon CloudWatch, which collects and processes raw data from Amazon RDS into readable, near real-time metrics. Open the [Amazon RDS service console](https://console.aws.amazon.com/rds/home) and click on [Databases](https://console.aws.amazon.com/rds/home#databases:) from left navigation pane. From list of databases click on auroralab-mysql-node-1 under *DB identifier*. On the database details view, click on the *Monitoring* tab and pick cloudwatch metrics from Monitoring.

<screenshot>

We can see that the base metrics like *CPU, DB connections, write latency,* *Read latency* and many more are spiking up for the same period. You can click on a chart to drill down for more details, select any chart area to zoom in on a specific time period.
[Image: Screenshot 2021-05-03 at 23.11.39.png]
During performance issues, although all the metrics are important its ideal to look at CPU,DB Connections,DML/DDL metrics.

(add the screenshots)

Amazon Aurora also provides a range of [CloudWatch metrics](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraMySQL.Monitoring.Metrics.html) populated with various database status variables. Let’s take a look at *DML metrics (*using the search bar*)* for this period and see how to interpret it.

In general

* Database activity variables responsible for tracking *throughput* are modified when the statement is received by the server.
* Database activity variables responsible for tracking *latency* are modified after the statement completes. This is quite intuitive: statement latency (i.e. execution time) is not known until the statement finishes.

[Image: Screenshot 2021-05-03 at 23.15.02.png][Image: Screenshot 2021-05-03 at 23.13.12.png]
*Note:*To learn more about how to plan for Aurora monitoring and Performance guidelines please refer our doc (https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/MonitoringOverview.html). 

DMLLatency metric reveals a spike at 22:57, when the metric reached 4442 milliseconds. In other words, 4.4 seconds is the average latency of all DML statements that finished during this 1-minute period. 4 seconds is significantly higher than the baseline latency observed before the spike, therefore it’s worth investigating.

A useful piece of information readily available from DMLThroughput metric . At 22.57 DML throughput is 0.907 which is roughly 54 operations. This could be the reason for the DML latency we noticed before.

```shell

.907 Operations
     ---------- X 60s= 54.42 ~ 54 operations
        s
```

*Optional:* Once the performance baseline is understood you can setup alarms against CW metrics when it exceeds the baseline for corrective actions.

### Enhanced Monitoring

You must have noticed that the CW metrics didn’t start populating right away as it takes 60 seconds interval period to capture data points. However to monitor and understand OS metrics eg. if the CPU is consumed by user or system, free/active memory for as granular as 1 second interval, then Enhanced Monitoring(EM) should help.

If you have Enhanced Monitoring option enabled for the database instance, select *Enhanced Monitoring* option from the *Monitoring* dropdown list.For more information about enabling and using the Enhanced Monitoring feature, please refer to the [Enhanced Monitoring doc](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/USER_Monitoring.OS.html).

You will see additional counters showing metrics captured at the guest OS level as well as local storage (not Aurora storage) .
[Image: Screenshot 2021-04-30 at 21.20.33.png]

From the above, the CPU is driven by *user* and *drop* in Free memory for the same period where there is Increase in *Load average 1 min.*

### Doing more with performance insights

#### Identify *top* SQL queries using performance insights dashboard.

Amazon RDS Performance Insights monitors your Amazon RDS DB instance load so that you can analyze and troubleshoot your database performance. To view the current performance insights dashboard, please go to the [RDS console](https://console.aws.amazon.com/rds/) and in the navigation pane, click performance insights and choose the writer node. You should see the console like below.  

[Image: Screenshot 2021-04-21 at 16.42.32.png]

The dashboard is divided into 3 sections, allowing you to drill down from high level performance indicator metrics down to individual *queries*, *waits*, *users* and *hosts* generating the load. You can learn more about this in the [previous lab](https://awsauroralabsmy.com/provisioned/perf-insights/). 

So far so good we can see wait types, wait events and the top queries but can we do more with *P.I*? Let’s enable additional components on the *counter metrics* and also on the *Session Activity* preferences at the bottom. We will also slightly change the view of *Database Load.*

Let’s start by adding counters in the *Counter Metrics* under Manage Metrics. This collects metrics from *DB* like innodb_rows_read, threads_running and *OS* metrics like cpuUtilization total, user etc which adds valuable information on top of CW metrics.
[Image: Screenshot 2021-05-07 at 11.26.26.png]

Enable *slow_queries* under DB Metrics and *cpuUtilization*  *total* under OS metrics

[Image: Screenshot 2021-04-21 at 19.00.45.png]
[Image: Screenshot 2021-04-21 at 18.57.40.png]

Click Update graph and once done, the counter metrics should look like below. We can see the innodb rows read,cpu utilisation  and slow queries counters surged and stayed high for this period.

[Image: Screenshot 2021-05-21 at 19.19.03.png]

We could see the CPU spike of ~100% for the ~4 minute period and the number of rows read is *1+ million* for 4 min period and slow logs were getting logged for this duration.

Next change the view of *DB Load section* from “Slice by wait“ to ”Slice by SQL“ and show the top queries during this time . We could also see the the max number of available *vCPUs* is 2 but the current sessions exceeds the max vCPU and this in many cases would be driving factor for CPU/memory consumption. As a temporary workaround you may scale up the instance to improve the situation but it’s not a scalable solution.

[Image: Screenshot 2021-05-07 at 11.30.39.png]
[Image: Screenshot 2021-04-30 at 11.55.45.png]

*Note:* Amazon Aurora MySQL specific *wait events* are documented in the [Amazon Aurora MySQL Reference guide](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Reference.html#AuroraMySQL.Reference.Waitevents).

Now let’s modify the *Session activity* part. The default interface for Top SQL contains AAS and SQL statements should look like this. Please go to the preferences section(gear icon at the right hand bottom) and add additional columns components.

[Image: Screenshot 2021-05-06 at 22.35.29.png]

To understand the performance profile it’s important to have additional information about the query access pattern. For the purpose of this lab, please enable Rows affected/sec,Rows affected/call,Rows examined/sec,Rows examined/call,Rows sent/sec,Rows sent/call and click *save*.

[Image: Screenshot 2021-05-21 at 14.49.13.png]

[Image: Screenshot 2021-05-21 at 14.49.24.png]

Once saved, the session activity for Top SQL would look like below. You should be able to see *rows examined/s* vs *rows sent/s* and corresponding *avg. latency* in ms/call. It would be ideal to focus on the queries with large difference between rows examined and rows sent . 

[Image: Screenshot 2021-05-21 at 16.46.18.png]

*Note:* To see the queries inside the stored procedure, please click and expand the + icon.

You can note down the top SQL queries but please keep in mind not all TOP SQL queries are slow queries it only means that these queries are consuming the load at given point of time.

As you noticed we can see performance insights are very good to understand average activity sessions however if you would like to get individual query stats/execution time then we should seek slow query logs. 


## 3 View *slow* queries 

### View and download slow query logs using the console

Lets’ view the slow query logs using the console . Since we ran the above script using the cluster endpoint(which points to the writer node by default), we should check the writer node logs. You can open the Amazon [RDS service console](https://console.aws.amazon.com/rds/home#database:id=auroralab-mysql-cluster;is-cluster=true;tab=monitoring) and click the cluster and select the writer node. Once selected, under *Logs & Events* scroll down to the *Logs* section. You should see like below.
[Image: Screenshot 2021-05-21 at 19.03.08.png]

You can select the slow query log for the timeframe and *view*/*watch* it and it should look like below if opted to *view*. 
[Image: Screenshot 2021-05-21 at 19.05.49.png]

You should see slow queries in the console. The log file content will have the following
 
*Query_time*: The statement execution time in seconds.
*Lock_time*: The time to acquire locks in seconds.
*Rows_sent*: The number of rows sent to the client.
*Rows_examined*: The number of rows examined by the server layer (not counting any processing internal to storage engines).

To learn more about slow queries, please check the [official doc](https://dev.mysql.com/doc/refman/5.7/en/slow-query-log.html). ** 

You can download the logs via *console* or *CLI* using [download-db-log-file-portion](https://docs.aws.amazon.com/cli/latest/reference/rds/download-db-log-file-portion.html). For now, let’s call this log as *slow_query_log1*.

*Note:* Log gets rotated hourly so please ensure the logs are downloaded for the workload period.

###  Leveraging CloudWatch logs and Log insights to view and analyze slow queries

Slow logs are great for troubleshooting but viewing/downloading individual logs could be time consuming. Also the logs could get rotated(if log_output= FILE) periodically. In addition to viewing and downloading DB instance logs from the console, you can *publish* logs to Amazon CloudWatch Logs . With CloudWatch Logs, you can perform real-time analysis of the log data, store and retain the data in highly durable storage, and manage the data with the CloudWatch Logs Agent.

We have already *enabled* export Cloudwatch logs option when we created the cluster. This can be verified by going to the RDS console, under cluster *configuration→ Published logs* like below. Please proceed to next step only if you see slow query  in it.

[Image: Screenshot 2021-04-30 at 10.03.17.png]

*Note:* To enable/disable these logs or add additional logs, you can click *Modify* at the *right top → Log exports → tick/untick prefered logs → continue → modify cluster.*

[Image: Screenshot 2021-04-30 at 13.02.34.png]
 
You can also verify the status of CloudWatch export and the type of logs thats currently enabled for export by executing the *CLI* below on the session manager terminal.

```shell
aws rds describe-db-clusters --db-cluster-identifier auroralab-mysql-cluster --query DBClusters[*].EnabledCloudwatchLogsExports
```
You should see the output like below. This sample output shows that currently export CloudWatch logs option is enabled for error logs and slow query logs.
[Image: Screenshot 2021-04-20 at 10.25.32.png]

###  View exported logs in CloudWatch

After enabling Aurora MySQL log events, you can monitor the events in Amazon CloudWatch Logs. A new log group is automatically created for the Aurora DB cluster under the following prefix, in which cluster-name represents the DB cluster name, and log_type represents the log type.

/aws/rds/cluster/cluster-name/log_type

For our DB cluster auroralab-mysql-cluster, slow query data is stored in the /aws/rds/cluster/auroralab-mysql-cluster/slowquery log group. Open the [Amazon Cloudwatch](https://console.aws.amazon.com/cloudwatch/home?p=clw&cp=bn&ad=c) console and select *Log groups* on the left hand side and search for auroralab-mysql-cluster/slowquery and it should see like below

[Image: Screenshot 2021-05-21 at 19.27.40.png]
Under *Log streams*, pick your current *writer* node (since that is where we ran our script against) to view the slow query logs and you should see like below
[Image: Screenshot 2021-04-30 at 13.06.00.png]

*Note:* The default log retention period is *Never Expire* however this can be changed*. Please see* *Change log data retention in CloudWatch Logs* (https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/SettingLogRetention.html)*.*

To increase the readability of these logs, we are going to use *Insights*. Click on the *insights* and select your log group in the drop down list. For slow queries, it will be in the format of /aws/rds/cluster/auroralab-mysql-cluster (https://eu-west-1.console.aws.amazon.com/rds/home?region=eu-west-1#database:id=auroralab-mysql-cluster;is-cluster=true;tab=logs-and-events)/slowquery. In the text field, enter the following insights query by replacing the <writer node>

```shell
filter @logStream = 'auroralab-mysql-node-1'
| parse @message "# Time: * User@Host: * Id: * Query_time: * Lock_time: * Rows_sent: * Rows_examined: * timestamp=*;*" as Time, User, Id, Query_time,Lock_time,Rows_sent,Rows_examined,timestamp,Query
| display Time, Query_time, Query,Rows_sent,Rows_examined
| sort Query_time asc
```

This query parses the slow query logs and captures the individual fields like *Time, Query_time, Query,Rows_sent,Rows_examined*. Once entered and *Run query*, the output should look something like below.

[Image: Screenshot 2021-05-04 at 19.00.42.png]

The queries listed are the offending queries which takes longer than the *long_query_time*. We could see around 100+ entries in the last 30 minutes.You can select any query to expand to find more information about it.

[Image: Screenshot 2021-05-04 at 19.00.57.png]

 You can also export the results to *csv* for easier analysis.For now let’s call it as *slow_query_log2*.

[Image: Screenshot 2021-04-21 at 16.18.24.png]

### Percona pt-query-digest 

*One challenge is that it requires manual effort or some automation technique to find unique patterns/queries from the slow queries logs and it could be challenging with thousands of logs. In order to find the unique queries, there are several third party tools and one of them is percona’s pt-query-digest which is helpful to solve this problem.*

Disclaimer: Percona pt-query-digest is a third party software licensed under GNU so please use [official documentation](https://www.percona.com/doc/percona-toolkit/2.0/pt-query-digest.html) for reference.

*pt-query-digest * is a open source tool from percona which analyzes MySQL queries from slow, general, and binary log files. You can learn more about this tool and download it from [here](https://www.percona.com/doc/percona-toolkit/LATEST/installation.html).

In short, this tool summaries the top queries based on the input log file ranked by response time. This is a two step process. 

*Step1:* First you need to download the *slow query logs* on the client. You can either do this over the *console* or *CLI*

#### Download using console

[Image: Screenshot 2021-05-03 at 11.39.47.png]

*Note:* Log gets rotated hourly so please ensure the logs are downloaded for the workload period.

#### Download using cli*

*CLI example*

```shell
aws rds download-db-log-file-portion --db-instance-identifier [writerendpoint] \
--starting-token 0 --output text --log-file-name slowquery/<slowlogname> > slow_log.txt
```

*Step2:*Once downloaded, you can run the pt-query-digest like below using the slow query log file we just downloaded.Please ensure the log name is correct.

```shell
$ pt-query-digest <slow_log_file.txt>
```

(1) This is a highly summarized view of the unique events in the detailed query report that follows. It contains the following columns and basically ranks the top offending queries and rank them from the slow query log which is easier to

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

[Image: Screenshot 2021-05-04 at 19.05.05.png]
For the queries listed above in the previous section, this section contains individual metrics about each query ID with stats like concurrency(calculated as a function of the timespan and total Query_time), exec time, rows sent, rows examine etc. This also provides the number of occurrences of a query in the log.
[Image: Screenshot 2021-05-04 at 19.05.20.png]


## 4 Analyze the queries using EXPLAIN and PROFILE

In this section, we are going to use the slow queries we captured in the previous sections and use them to investigate with the help of *EXPLAIN* and *PROFILE*.

So far we have *3* *slow_query_log files and for the purpose of the lab, let’s use slow_query_log3. *You can also use *slow_query_log1* or *slow_query_log2* but you need to identify the *unique* queries across the logs*. Once identified the slow query log file should contain the below queries.*

For the purpose of the lab, lets call this as *slow_query_final.log*

```SQL
[Q1] UPDATE mylab.weather SET max_temp = 31 where id='USC00103882' ;
[Q2] CALL insert_temp ;
    INSERT INTO mylab.weather VALUES ('1993-12-10','14.38','USC00147271',-100.92,38.47,21.70,-4.40,'SCOTT CITY','Weak Hot',key_value);
    DELETE from mylab.weather  where serialid=key_value;
[Q3] SELECT sql_no_cache max_temp,min_temp,station_name FROM weather WHERE max_temp > 42 and id = 'USC00103882' ORDER BY max_temp DESC;
[Q4] SELECT sql_no_cache count(id) FROM weather WHERE station_name = 'EAGLE MTN' and type = 'Weak Cold';
[Q5] SELECT sql_no_cache station_name, count(type) type_of_weather FROM weather WHERE type = 'Strong Cold';
```

*Optional:* You can also go ahead and run the above queries individually on the terminal and see the individual response time.

### EXPLAIN plan


The [EXPLAIN](https://dev.mysql.com/doc/refman/5.7/en/explain.html) statement provides information about how MySQL executes statements. [EXPLAIN](https://dev.mysql.com/doc/refman/5.7/en/explain.html) works with [SELECT](https://dev.mysql.com/doc/refman/5.7/en/select.html), [DELETE](https://dev.mysql.com/doc/refman/5.7/en/delete.html), [INSERT](https://dev.mysql.com/doc/refman/5.7/en/insert.html), [REPLACE](https://dev.mysql.com/doc/refman/8.0/en/replace.html), and [UPDATE](https://dev.mysql.com/doc/refman/8.0/en/update.html) statements. With the help of [EXPLAIN](https://dev.mysql.com/doc/refman/5.7/en/explain.html), you can see where you should add indexes to tables so that the statement executes faster by using indexes to find rows.

Lets go ahead capture the explain plan for those queries listed above . You can use run the explain plan for a query like below

```sql
*EXPLAIN* query name.
```
Below is an explain plan for the [*Q5*]

```sql
EXPLAIN SELECT sql_no_cache max_temp,min_temp,station_name FROM weather WHERE max_temp > 42 and id = 'USC00103882' ORDER BY max_temp DE
SC ;
```

[Image: Screenshot 2021-04-30 at 14.53.18.png]
The explain plan has multiple fields and the most common ones to look at it are

* It was again a SELECT against the same table “weather”  using filesort.If an index cannot be used to satisfy an ORDER BY clause, MySQL performs a filesort operation that reads table rows and sorts them. A filesort constitutes an extra sorting phase in query execution.
* Fields “possible_keys” and “key” indicate that the table does not contain indexes that could be used during query execution.
* The “type” field proves that database would need to perform a full table scan to run the query i.e. would need to consider ALL rows.
* The “rows” field shows the number of rows to be scanned which is around 3M.

In this example, we see that the estimation of rows to be examined is very high and we can also see the absence of key for this.

*To learn more about EXPLAIN plan outputs you can refer to [link](https://dev.mysql.com/doc/refman/5.7/en/explain-output.html)*.*

*Hint:* you can also use [explain format=json](https://dev.mysql.com/doc/refman/5.7/en/explain-output.html)* if you are interested in understanding how subqueries are materialized.

Our earlier investigations says that query[5] is slow and P.I also suggested this query was one of the top consumers of resources. Let’s take a look at where this query is spending its time. In order to indentify that we can make use of [PROFILE](https://dev.mysql.com/doc/refman/5.7/en/show-profile.html).

### PROFILE

The SHOW [PROFILE](https://dev.mysql.com/doc/refman/5.7/en/show-profile.html) and [SHOW PROFILES](https://dev.mysql.com/doc/refman/5.7/en/show-profiles.html) commands display profiling information that indicates resource usage for statements executed during the course of the current session. Even though this can be obtained using performance schema this is widely used due to ease of use.

In order to perform profiling for the *[Q5]*, please run the below.

```shell
SET profiling = 1;
SELECT sql_no_cache count(id) FROM weather WHERE station_name = 'EAGLE MTN' and type = 'Weak Cold';
SHOW PROFILES;
SHOW PROFILE FOR QUERY 1;
SET profiling = 0;
```

the output should look like below. 
[Image: Screenshot 2021-05-04 at 13.13.39.png]
From this, we can see where this query is spending its resources. In this example, we can see its spending time on “*sending data*”. This means, the thread is reading and processing rows for a SELECT (https://dev.mysql.com/doc/refman/5.7/en/select.html) statement, and sending data to the client. Because operations occurring during this state tend to perform large amounts of disk access (reads), it is often the longest-running state over the lifetime of a given query.”Lets’ find out why it’s doing large amount of disk reads.

### Index presence

In order to do so, let’s check the *schema* in question to see if table have any indexes, so that we can use them in the queries to improve the read performance. The use of indexes to assist with large blocks of tables, data may have considerable impact on reducing MySQL query execution and, thus, overall CPU overhead. Non-indexed tables are nothing more than unordered lists; hence, the MySQL engine must search them from starting to end. This may have little impact when working with small tables, but may dramatically affect search time for larger tables.

Presence of index can be done by running one of the methods below:

*using DDL of the table*

We can check the DDL of the table to see if it has any indexes like show create table mylab.weather \G

```shell
mysql> show create table weather \G
       Table: weather
Create Table: CREATE TABLE weather (
  date_Str date NOT NULL COMMENT 'Date and Time of Readings',
  degres_from_mean varchar(100) DEFAULT NULL,
  id varchar(11) NOT NULL COMMENT 'station id',
  longitude decimal(5,2) NOT NULL COMMENT 'longitu',
  latitude decimal(5,2) NOT NULL COMMENT 'latitude',
  max_temp decimal(5,2) NOT NULL COMMENT 'max temp logged',
  min_temp decimal(5,2) NOT NULL COMMENT 'min temp logged',
  station_name varchar(50) NOT NULL COMMENT 'station names',
  type varchar(25) NOT NULL COMMENT 'station names',
  serialid int(11) NOT NULL COMMENT 'serial id of log'
) ENGINE=InnoDB DEFAULT CHARSET=latin1
1 row in set (0.01 sec)
```

From the above schema we can see the table does not have any *keys/indexes* and this explains why the queries are scanning huge number of rows and results in slowness.
```shell
using SHOW INDEX
```
Alternatively you can run show index from mylab.weather \G

```shell
mysql> show index from mylab.weather \G
Empty set (0.01 sec)
```
We can see that *mylab.weather* table does not have any primary keys. 


```shell
[Q1] UPDATE mylab.weather SET max_temp = 31 where id='USC00103882' ;
[Q2] CALL insert_temp ;
    INSERT INTO mylab.weather VALUES ('1993-12-10','14.38','USC00147271',-100.92,38.47,21.70,-4.40,'SCOTT CITY','Weak Hot',key_value);
    DELETE from mylab.weather  where serialid=key_value;
[Q3] SELECT sql_no_cache max_temp,min_temp,station_name FROM weather WHERE max_temp > 42 and id = 'USC00103882' ORDER BY max_temp DESC;
[Q4] SELECT sql_no_cache count(id) FROM weather WHERE station_name = 'EAGLE MTN' and type = 'Weak Cold';
```

## 6 Tune 

In real world, based on the type of wait events, schemas, resource utilisation the tuning approach varies.There are many ways you can take appropriate corrective actions like tune the server parameters, tune a query by re-writing it, tune the database schemas or even tune the code(App,DB). 

*Disclaimer: Since this is a lab environment, we have used our liberty to add indexes on the schema for tuning exercise as this does not requires us to touch the app or to rewrite the query.** However in real world, each use case differs and therefore its essential to fully understand the columns and its purpose and how your business logic is going to use it before adding indexes. always test the changes on test/staging environment before making it into production environment.*

In this section, we are going to take the queries from the  *slow_query_final.log *and we are going to take advantage of explain plan to understand the bottleneck and how to fix them. We will also compare the *plans* before and after fixing queries.


*[Q1] CALL update_temp ;*

```sql
UPDATE mylab.weather SET max_temp = 10.00 where id='USC00103882';
```

[*Q1*] , we can see that the queries are filtered using the column “*id*”. Lets check the explain plan of the query and the explain plan looks like below

```sql
  EXPLAIN UPDATE mylab.weather SET max_temp = 10.00 where id='USC00103882';
```

[Image: Screenshot 2021-05-21 at 19.32.15.png]From this, we can see the *absence* of keys and the number of rows *scanned* is high. Let’s try adding an index on this column and continue to investigate if this helps.
*_ADD INDEX_*

```sql
ALTER TABLE mylab.weather ADD index idx_id (id);
```

[Image: Screenshot 2021-04-30 at 15.03.44.png]After adding the index, lets check the explain plan. We can see that now the query is using our newly created id *idx_id* and the number of rows examined has been drastically reduced from *3M* to *1K*.
[Image: Screenshot 2021-05-03 at 12.00.56.png]Using the same logic, let’s add index to the field *serialid* for ** which we found inside the stored procedure *[Q2] .* Before that lets capture the explain plan and once index is added, lets capture the explain plan again.

```sql
EXPLAIN DELETE from mylab.weather where serialid=3150000;
ALTER TABLE weather ADD INDEX serialid (serialid) ;
EXPLAIN DELETE from mylab.weather where serialid=3150000;
```

Output should look like below.
[Image: Screenshot 2021-05-03 at 12.04.00.png]While we are at it, lets also check the Explain plan for [Q3]  before and after to see the impact of indexes on this.

```sql
[Q3] SELECT sql_no_cache max_temp,min_temp,station_name FROM weather WHERE max_temp > 42 and id = 'USC00103882' ORDER BY max_temp DESC\G
```

*Before index*
[Image: Screenshot 2021-05-21 at 19.36.42.png]*After index*
[Image: Screenshot 2021-04-30 at 15.12.26.png]
composite index

In [*Q4*], we can see *station_name* and *type* is used for filtering the results. As you know with MySQL we can use multiple-column indexes for queries that test all the columns in the index, or queries that test just the first column, the first two columns, the first three columns, and so on. composite indexes (that is, indexes on multiple columns) and keep in mind MySQL allows you to create composite index up to 16 columns.

```sql
[Q4] SELECT sql_no_cache count(id) FROM weather WHERE station_name = 'EAGLE MTN' and type = 'Weak Cold';
```

 Let's create a composite index for the '*station_name*' and '*type*' columns on table *weather* for [Q4]. Lets check the explain plan before and after adding indexes.

```sql
EXPLAIN SELECT sql_no_cache count(id) FROM weather WHERE station_name = 'EAGLE MTN' and type = 'Weak Cold' ;
ALTER TABLE mylab.weather ADD INDEX id_station_type (station_name, type);
EXPLAIN SELECT sql_no_cache count(id) FROM weather WHERE station_name = 'EAGLE MTN' and type = 'Weak Cold' ;
```

*Before Index*
[Image: Screenshot 2021-05-03 at 12.06.14.png]*After index*
[Image: Screenshot 2021-05-03 at 12.06.06.png]
By adding different indexes to the queries from the *slow_query_final.log,* we can see that *[Q1][Q2][Q3][Q4]* got ** benefited*.* 

_*RE-VIST PROFILE*_

While we are it, lets revisit the *PROFILING* to see if it has been changed after adding the index for [q5]. We already captured the profiling for [*Q4*] in the previous section . Let’s capture it again using the below query on the terminal.

```sql
SET profiling = 1;
SELECT sql_no_cache count(id) FROM weather WHERE station_name = 'EAGLE MTN' and type = 'Weak Cold';
SHOW PROFILES;
SHOW PROFILE FOR QUERY 1;
SET profiling = 0;
```

Once executed, this should look like below. We can see that compared to earlier snapshot, we could see the query is spending less time on “sending data“, which indicates the disk reads are much faster since it has to scan very few rows compared to earlier because of index.
[Image: Screenshot 2021-05-03 at 11.58.50.png]
We can see that the query which was spending time on *sending data* is not seen anymore after adding the index.

## 6 Performance review:

Now after adding the indexes, let’s *re-run* the script and compare and review the performance in whole for before and after. Before re-running the tests lets truncate the performance schema tables to have fresh counters. This would make our before vs after comparison much easier. Please run the commands below on the mysql terminal

Please re-run the test like below

```shell
python3 weather_perf.py -e[clusterendpoint] -u$DBUSER -p"$DBPASS" -dmylab
```

*First thing you would have noticed is that the script which took around 3.5 minutes earlier is now completed within 1 minute.*

Let’s take a look at CW metrics and we cannot see any peak periods compared to before.

[Image: Screenshot 2021-05-21 at 19.56.27.png]<add screenshots>(should I include this?)

[Image: Screenshot 2021-05-21 at 19.56.39.png]

Let’s take a look at *EM metrics* and we can see there are no peak periods compared to before.

[Image: Screenshot 2021-05-21 at 19.58.56.png]

*Let’s take a look at slow query logs*

We can see that the query time has been drastically reduced and the number of rows examined is also reduced from *1M* to less than *1K* rows.
[Image: Screenshot 2021-05-21 at 19.54.31.png]
Let’s take a revisit at the *performance schema* metrics. As you could see from the screenshot, the execution time is no longer than 1 minute as compared to around 4 minutes before adding the index.

From the counter metrics, we can see earlier the number of rows scanned is *1.2+M* however now this has come down to only *1.6K .* The CPU total consumption is at a *baseline* average and CPU spike is not visible now. Also there are hardly any slow query log entries.
[Image: Screenshot 2021-05-04 at 19.21.09.png]We can see that earlier we has sessions exceeding max vCPUs however the execution was rather quick and didn’t throttle the CPU. This also means our solution worked *without scaling up* the instance.

[Image: Screenshot 2021-05-21 at 19.50.12.png]
We can also see from the top SQL, the queries which appeared before adding indexes are not appearing anymore. This indicates that indexes helps those queries in consuming less resources and therefore they do not appear as top SQL queries.
[Image: Screenshot 2021-05-21 at 19.51.18.png]

We have used :

* RDS monitoring tools like CW metrics, EM monitoring and OS Processlist to understand the workload pattern
* RDS performance monitoring tools like Performance Insights and its counters to understand the workload
* RDS MySQL logs and AWS tools like CW logs and insights to identify the slow query logs and understand the pattern of  queries.
* MySQL processlist, innodb status, locking info,Explain plan and profile to analyze the slow queries we captured above
* Fine tune by adding indexes to improve the performance without rewriting the query or rewriting the app.


## Optional:

### Performance Schema

The Performance Schema(*P_S*) is an advanced MySQL diagnostic tool for monitoring MySQL Server. Due to certain CPU and memory overhead, Performance schema is *disabled* by default. However when performance insights is enabled, performance schema is automatically enabled by default. 

As a background, performance insights uses performance schema and other global counters to construct the visualisation metrics. So without Performance Insights (P.I), we can still able to gather valuable information with the help of performance schema. ** If you would like to learn how to enable performance schema seperately without having perfomrance insights please refer our official doc (http://Enabling the Performance Schema for Performance Insights on Aurora MySQL) for step by step instructions.

*P_S* feature works by counting and timing server events and gathers in memory and expose them through a collection of tables in the performance schema database. 

Let’s use [events_statements_summary_global_by_event_name](https://dev.mysql.com/doc/refman/5.7/en/performance-schema-statement-summary-tables.html) and [events_statements_summary_by_digest](https://dev.mysql.com/doc/refman/5.7/en/performance-schema-statement-summary-tables.html)  table to capture top queries, events etc

*Note:* Performance Schema tables are kept in memory and their contents will be lost in the event of server reboot. 

#### Syntax (top 5, wait events)

```sql
select event_name as wait_event, count_star as all_occurrences, CONCAT(ROUND(sum_timer_wait / 1000000000000, 2), ' s') as total_wait_time, CONCAT(ROUND(avg_timer_wait / 1000000000000, 2), ' s') as avg_wait_time from performance_schema.events_waits_summary_global_by_event_name where count_star > 0 and event_name <> 'idle' order by sum_timer_wait desc limit 5;
```

#### Syntax (top 5 statements, order by total execution time)

```sql
select replace(event_name, 'statement/sql/', '') as statement, count_star as all_occurrences, CONCAT(ROUND(sum_timer_wait / 1000000000000, 2), ' s') as total_latency, CONCAT(ROUND(avg_timer_wait / 1000000000000, 2), ' s') as avg_latency, CONCAT(ROUND(sum_lock_time / 1000000000000, 2), ' s') as total_lock_time, sum_rows_affected as sum_rows_changed, sum_rows_sent as sum_rows_selected, sum_rows_examined as sum_rows_scanned, sum_created_tmp_tables, sum_created_tmp_disk_tables, if(sum_created_tmp_tables = 0, 0, concat(truncate(sum_created_tmp_disk_tables/sum_created_tmp_tables*100, 0))) as tmp_disk_tables_percent, sum_select_scan, sum_no_index_used, sum_no_good_index_used from performance_schema.events_statements_summary_global_by_event_name where event_name like 'statement/sql/%' and count_star > 0 order by sum_timer_wait desc limit 5;
```
#### Syntax (top 5 queries, order by total execution time):

```sql
select digest_text as normalized_query, count_star as all_occurr, CONCAT(ROUND(sum_timer_wait / 1000000000000, 3), ' s') as total_t, CONCAT(ROUND(min_timer_wait / 1000000000000, 3), 's') as min_t, CONCAT(ROUND(max_timer_wait / 1000000000000, 3), ' s') as max_t, CONCAT(ROUND(avg_timer_wait / 1000000000000, 3), ' s') as avg_t, CONCAT(ROUND(sum_lock_time / 1000000000000, 3), ' s') as total_lock_t, sum_rows_affected as sum_rows_changed, sum_rows_sent as sum_rows_selected, sum_rows_examined as sum_rows_scanned, sum_created_tmp_tables, sum_created_tmp_tables, sum_select_scan, sum_no_index_used from performance_schema.events_statements_summary_by_digest where schema_name iS NOT NULL order by sum_timer_wait desc limit 5 ;
```

#### Syntax (top 5 queries performing Full table scan)
```sql
SELECT schema_name, substr(digest_text, 1, 100) AS statement, count_star AS cnt, sum_select_scan AS full_table_scan FROM performance_schema.events_statements_summary_by_digest WHERE sum_select_scan > 0 and schema_name iS NOT NULL ORDER BY sum_select_scan desc limit 5;
```
*Note:* Before every load, to get fresh counters you can consider truncating the performance schema tables that you want to query.

####Syntax (top 5 queries for which Temporary tables spilled to disk)

```sql
mysql> SELECT schema_name, substr(digest_text, 1, 100) AS statement,count_star AS cnt, sum_created_tmp_disk_tables AS tmp_disk_tables,sum_created_tmp_tables AS tmp_tables FROM performance_schema.events_statements_summary_by_digest WHERE sum_created_tmp_disk_tables > 0 OR sum_created_tmp_tables >0 and schema
_name='mylab' ORDER BY tmp_disk_tables desc limit 5;
```

*Note:* To learn more about abour *Statement Digest aggregation rules* please refer [official doc](https://dev.mysql.com/doc/refman/5.7/en/performance-schema-statement-summary-tables.html#statement-summary-tables-aggregation).


### Understand the workload

#### Processlist 
To get an idea about workload you can run *show process-list* to see active transactions, idle/sleep transactions etc

```sql
SHOW PROCESSLIST:
```

#### Innodb Status
To understand transactions running inside dbengine, you can run [SHOW ENGINE INNODB STATUS](https://dev.mysql.com/doc/refman/5.7/en/show-engine.html) on the writer note. Please note this query works only on the writer and not on the reader. This command exposes outputs from various InnoDB monitors and can be instrumental in understanding the internal state of InnoDB engine. Information returned by the command includes but is not limited to:

* Details of most recently detected deadlocks and foreign key errors,
* Transactions and their activity,
* State of InnoDB memory structures such as the Buffer Pool and Adaptive Hash Index.

```sql
SHOW ENGINE INNODB STATUS \G
```
#### Locking information

To understand locking transactions you can query [information_schema](https://dev.mysql.com/doc/refman/5.7/en/innodb-information-schema-examples.html) like below..

```sql
SELECT r.trx_id waiting_trx_id, r.trx_mysql_thread_id waiting_thread, r.trx_query waiting_query, b.trx_id blocking_trx_id, b.trx_mysql_thread_id blocking_thread, b.trx_query blocking_query FROM information_schema.innodb_lock_waits w INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;
```

[Image: Screenshot 2021-05-03 at 22.59.19.png] With Aurora blocking transactions can be monitored through BlockedTransactions and deadlocks through [Deadlocks CW metrics](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraMySQL.Monitoring.Metrics.html) which might be helpful. You can enable the parameter innodb_print_all_deadlocks to have all deadlocks in InnoDB recorded in mysqld error log.
