# Aurora MySQL SQL Performance Troubleshooting - Analysis (WIP)

In this lab, we are going to demonstrate *how to troubleshoot SQL performance related issues* using different tools. Specifically we are going to look at how you can leverage *EXPLAIN, PROFILE, performance_schema*  to analyze the query. Also we are going to briefly shows how indexes can help in improving the performance of your query.

This lab contains the following tasks:

* *Analyse* the slow queries using MySQL *Explain* plan, *profiling*
* *Tune* the Queries
* *Performance Review*

*Optional:* Performance Schema

This lab requires the following prerequisites:

* [Aurora MySQL SQL Performance Troubleshooting - Observability](/provisioned/sql_perf_observability/)


## 1. Analyze the queries using EXPLAIN and PROFILE

In this section, we are going to use the slow queries we captured in the previous sections and use them to investigate with the help of *EXPLAIN* and *PROFILE*. So far we have *3 slow_query_log* files and for the purpose of the lab, let’s use *slow_query_log3*. *You may also use *slow_query_log1* or *slow_query_log2* but you need to identify the *unique* queries across the logs*. Once identified, the slow query log file should contain the below queries.

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

Let's go ahead capture the explain plan for those queries listed above . You can use run the explain plan for a query like below

```sql
*EXPLAIN* query name.
```
Below is an explain plan for the [*Q5*]

```sql
EXPLAIN SELECT sql_no_cache max_temp,min_temp,station_name FROM weather WHERE max_temp > 42 and id = 'USC00103882' ORDER BY max_temp DESC ;
```

<span class="image">![Explain](explain_before_index_1.png?raw=true)</span>

The explain plan has multiple fields and the most common ones to look at it are

* It was again a SELECT against the same table “weather”  using filesort.If an index cannot be used to satisfy an ORDER BY clause, MySQL performs a filesort operation that reads table rows and sorts them. A filesort constitutes an extra sorting phase in query execution.
* Fields “possible_keys” and “key” indicate that the table does not contain indexes that could be used during query execution.
* The “type” field proves that database would need to perform a full table scan to run the query i.e. would need to consider ALL rows.
* The “rows” field shows the number of rows to be scanned which is around 3M.

In this example, we see that the estimation of rows to be examined is very high and we can also see the absence of key for this.

*To learn more about EXPLAIN plan outputs you can refer to [link](https://dev.mysql.com/doc/refman/5.7/en/explain-output.html)*.*

*Hint:* you can also use [explain format=json](https://dev.mysql.com/doc/refman/5.7/en/explain-output.html)* if you are interested in understanding how subqueries are materialized.

Our earlier investigations says that query[5] is slow and P.I also suggested this query was one of the top consumers of resources. Let’s take a look at where this query is spending its time. In order to indentify that we can make use of [PROFILE](https://dev.mysql.com/doc/refman/5.7/en/show-profile.html).

### PROFILING

#### Option 1:PROFILE

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

<span class="image">![PROFILE](profile_before_index.png?raw=true)</span>


From this, we can see where this query is spending its resources. In this example, we can see it's spending time on “*sending data*”. This means, the thread is reading and processing rows for a SELECT (https://dev.mysql.com/doc/refman/5.7/en/select.html) statement, and sending data to the client. Because operations occurring during this state tend to perform large amounts of disk access (reads), it is often the longest-running state over the lifetime of a given query.”Lets’ find out why it’s doing large amount of disk reads.

#### Option 2:Query Profiling using Performance Schema

The SHOW PROFILE and SHOW PROFILES statements are deprecated and the following example demonstrates how to use [Performance Schema](https://dev.mysql.com/doc/refman/5.7/en/performance-schema.html) statement events and stage events to retrieve data comparable to profiling information provided by SHOW PROFILES and SHOW PROFILE statement.

hint: You can learn more about how to performance schema at the bottom of this exercise

Ensure that statement and stage instrumentation is enabled by updating the setup_instruments table. Some instruments may already be enabled by default.

```SQL
UPDATE performance_schema.setup_instruments SET ENABLED = 'YES', TIMED = 'YES' WHERE NAME LIKE '%statement/%';

UPDATE performance_schema.setup_instruments SET ENABLED = 'YES', TIMED = 'YES' WHERE NAME LIKE '%stage/%';
```
<span class="image">![profile_setup_instruments](PI_setup_instruments.png?raw=true)</span>


Ensure that events_statements_* and events_stages_* consumers are enabled. Some consumers may already be enabled by default.

```SQL
UPDATE performance_schema.setup_consumers SET ENABLED = 'YES' WHERE NAME LIKE '%events_statements_%';

UPDATE performance_schema.setup_consumers SET ENABLED = 'YES' WHERE NAME LIKE '%events_stages_%';
```
<span class="image">![profile_setup_consumers](PI_setup_consumers.png?raw=true)</span>


Please run the statement that you want to profile. For example:

```SQL
SELECT sql_no_cache count(id) FROM weather WHERE station_name = 'EAGLE MTN' and type = 'Weak Cold';
```
<span class="image">![profile_query](PI_prof_query.png?raw=true)</span>


Identify the EVENT_ID of the statement by querying the events_statements_history_long table. This step is similar to running SHOW PROFILES to identify the Query_ID. The following query produces output similar to SHOW PROFILES:

```SQL
SELECT EVENT_ID, TRUNCATE(TIMER_WAIT/1000000000000,6) as Duration, SQL_TEXT FROM performance_schema.events_statements_history_long WHERE SQL_TEXT like '%EAGLE MTN%';
```
<span class="image">![profile_query_ID](PI_prof_query_ID.png?raw=true)</span>


Query the events_stages_history_long table to retrieve the statement's stage events. Stages are linked to statements using event nesting. Each stage event record has a NESTING_EVENT_ID column that contains the EVENT_ID of the parent statement.

```SQL
SELECT event_name AS Stage, TRUNCATE(TIMER_WAIT/1000000000000,6) AS Duration FROM performance_schema.events_stages_history_long WHERE NESTING_EVENT_ID=EVENT_ID;
```
<span class="image">![profile_query_result](PI_prof_result.png?raw=true)</span>


**Note:** The setup_actors table can be used to limit the collection of historical events by host, user, or account to reduce runtime overhead and the amount of data collected in history tables. If you want fresh counters you can truncate and start the collection again like below:

```SQL
mysql> truncate performance_schema.events_stages_history_long;
mysql> truncate performance_schema.events_statements_history_long;
```

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

## 2. Tune

In real world, based on the type of wait events, schemas, resource utilisation the tuning approach varies.There are many ways you can take appropriate corrective actions like tune the server parameters, tune a query by re-writing it, tune the database schemas or even tune the code(App,DB).

*Disclaimer: Since this is a lab environment, we have used our liberty to add indexes on the schema for tuning exercise as this does not requires us to touch the app or to rewrite the query.** However in real world, each use case differs and therefore its essential to fully understand the columns and its purpose and how your business logic is going to use it before adding indexes. always test the changes on test/staging environment before making it into production environment.*

In this section, we are going to take the queries from the  *slow_query_final.log *and we are going to take advantage of explain plan to understand the bottleneck and how to fix them. We will also compare the *plans* before and after fixing queries.

### Index
*[Q1] CALL update_temp ;*

```sql
UPDATE mylab.weather SET max_temp = 10.00 where id='USC00103882';
```

[*Q1*] , we can see that the queries are filtered using the column “*id*”. Lets check the explain plan of the query and the explain plan looks like below

```sql
  EXPLAIN UPDATE mylab.weather SET max_temp = 10.00 where id='USC00103882';
```

 <span class="image">![Tune](explain_before_simple.png?raw=true)</span>

From this, we can see the *absence* of keys and the number of rows *scanned* is high. Let’s try adding an index on this column and continue to investigate if this helps.

*_ADD INDEX_*

```sql
ALTER TABLE mylab.weather ADD index idx_id (id);
```

<span class="image">![Tune](alter.png?raw=true)</span>

After adding the index, lets check the explain plan. We can see that now the query is using our newly created id *idx_id* and the number of rows examined has been drastically reduced from *3M* to *1K*.

  <span class="image">![Tune](explain_after_simple.png?raw=true)</span>


Using the same logic, let’s add index to the field *serialid* for ** which we found inside the stored procedure *[Q2] .* Before that lets capture the explain plan and once index is added, lets capture the explain plan again.

```sql
EXPLAIN DELETE from mylab.weather where serialid=3150000;
ALTER TABLE weather ADD INDEX serialid (serialid) ;
EXPLAIN DELETE from mylab.weather where serialid=3150000;
```

Output should look like below.

<span class="image">![Tune](explain_before_After.png?raw=true)</span>

While we are at it, lets check the Explain plan for [Q3] before and after to see the impact of indexes on this.

```sql
[Q3] SELECT sql_no_cache max_temp,min_temp,station_name FROM weather WHERE max_temp > 42 and id = 'USC00103882' ORDER BY max_temp DESC\G
```

*Before index*

<span class="image">![Tune](explain_before_index_1.png?raw=true)</span>

*After index*

<span class="image">![Tune](explain_after_index_1.png?raw=true)</span>

### Composite Index

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

<span class="image">![Tune](explain_composite_before_index.png?raw=true)</span>

*After index*

<span class="image">![Tune](explain_composite_after_index.png?raw=true)</span>

By adding different indexes to the queries from the *slow_query_final.log,* we can see that *[Q1][Q2][Q3][Q4]* got ** benefited*.*

### Re-visit PROFILE

While we are it, lets revisit the *PROFILING* to see if it has been changed after adding the index for [q5]. We already captured the profiling for [*Q4*] in the previous section . Let’s capture it again using the below query on the terminal.

#### Option 1:PROFILE

```sql
SET profiling = 1;
SELECT sql_no_cache count(id) FROM weather WHERE station_name = 'EAGLE MTN' and type = 'Weak Cold';
SHOW PROFILES;
SHOW PROFILE FOR QUERY 1;
SET profiling = 0;
```

Once executed, this should look like below. We can see that compared to earlier snapshot, we could see the query is spending less time on “sending data“, which indicates the disk reads are much faster since it has to scan very few rows compared to earlier because of index.

<span class="image">![Tune](profile_after_index.png?raw=true)</span>

#### Option 2:Query Profiling using Performance Schema


<span class="image">![Tune](PI_prof_after_index.png?raw=true)</span>


In both cases, we can see that the query which was spending time on *sending data* is not seen anymore after adding the index.

## Performance review

Now after adding the indexes, let’s *re-run* the script and compare and review the performance in whole for before and after. Before re-running the tests lets truncate the performance schema tables to have fresh counters. This would make our before vs after comparison much easier. Please run the commands below on the mysql terminal

Please re-run the test like below

```shell
python3 weather_perf.py -e[clusterendpoint] -u$DBUSER -p"$DBPASS" -dmylab
```

*First thing you would have noticed is that the script which took around 3.5 minutes earlier is now completed within 1 minute.*

Let’s take a look at **CW metrics** and we cannot see any peak periods compared to before.

<span class="image">![Perf Review](CW_after_index.png?raw=true)</span>

Let’s take a look at **slow query logs**.We can see that the query time has been *drastically reduced* and the number of rows examined is also reduced from *1M* to less than *1K* rows.

<span class="image">![Perf Review](perf4.png?raw=true)</span>

From the counter metrics, we can see earlier the number of rows scanned is *1.2+M* however now this has come down to only *1.6K .* The CPU total consumption is at a *baseline* average and CPU spike is not visible now. Also there are *hardly any slow query log entries*.

<span class="image">![Perf Review](P.I_review_after_index.png?raw=true)</span>

<span class="image">![Perf Review](P.I_review_counter_after_index.png?raw=true)</span>

We can see that earlier we has sessions exceeding **max vCPUs** however the execution was rather quick and didn’t throttle the CPU. This also means our solution worked *without scaling up* the instance.

<span class="image">![Perf Review](P.I_review_DBload_after_index.png?raw=true)</span>

We can also see from the top SQL, the queries which appeared before adding indexes are not appearing anymore. This indicates that indexes helps those queries in consuming less resources and therefore they do not appear as top SQL queries.

<span class="image">![Perf Review](P.I_review_top_after_index.png?raw=true)</span>

We have used :

* RDS monitoring tools like CW metrics, EM monitoring and OS Processlist to understand the workload pattern
* RDS performance monitoring tools like Performance Insights and its counters to understand the workload
* RDS MySQL logs and AWS tools like CW logs and insights to identify the slow query logs and understand the pattern of  queries.
* MySQL processlist, innodb status, locking info,Explain plan and profile to analyze the slow queries we captured above
* Fine tune by adding indexes to improve the performance without rewriting the query or rewriting the app.


## 4. Optional:

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
mysql> SELECT schema_name, substr(digest_text, 1, 100) AS statement,count_star AS cnt, sum_created_tmp_disk_tables AS tmp_disk_tables,sum_created_tmp_tables AS tmp_tables FROM performance_schema.events_statements_summary_by_digest WHERE sum_created_tmp_disk_tables > 0 OR sum_created_tmp_tables >0 and schema_name='mylab' ORDER BY tmp_disk_tables desc limit 5;
```

*Note:* To learn more about *Statement Digest aggregation rules* please refer [official doc](https://dev.mysql.com/doc/refman/5.7/en/performance-schema-statement-summary-tables.html#statement-summary-tables-aggregation).


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
Output should look something like below

<span class="image">![InnoDB Status](InnoDB_stat1.png?raw=true)</span>


<span class="image">![InnoDB Status](InnoDB_stat2.png?raw=true)</span>


<span class="image">![InnoDB Status](InnoDB_stat3.png?raw=true)</span>

The following [sections](https://mariadb.com/kb/en/show-engine-innodb-status/) are displayed

* **SEMAPHORES:** Threads waiting for a semaphore and stats on how the number of times threads have needed a spin or a wait on a mutex or rw-lock semaphore. If this number of threads is large, there may be I/O or contention issues. Reducing the size of the innodb_thread_concurrency system variable may help if contention is related to thread scheduling. Spin rounds per wait shows the number of spinlock rounds per OS wait for a mutex.

* **LATEST FOREIGN KEY ERROR:** Only shown if there has been a foreign key constraint error, it displays the failed statement and information about the constraint and the related tables.

* **LATEST DETECTED DEADLOCK:** Only shown if there has been a deadlock, it displays the transactions involved in the deadlock and the statements being executed, held and required locked and the transaction rolled back to.

* **History list length:** Unpurged old row versions from undo logs.

* **TRANSACTIONS:** The output of this section can help identify lock contention, as well as reasons for the deadlocks.

* **BUFFER POOL AND MEMORY:** Information on buffer pool pages read and written, which allows you to see the number of data file I/O operations performed by your queries. See InnoDB Buffer Pool for more. Similar information is also available from the INFORMATION_SCHEMA.INNODB_BUFFER_POOL_STATS table.

* **ROW OPERATIONS:** Information about the main thread, including the number and performance rate for each type of row operation. Would give a snapshot of whether the instance is read or write heavy.

#### Locking information

To understand locking transactions you can query [information_schema](https://dev.mysql.com/doc/refman/5.7/en/innodb-information-schema-examples.html) like below..

```sql
SELECT r.trx_id waiting_trx_id, r.trx_mysql_thread_id waiting_thread, r.trx_query waiting_query, b.trx_id blocking_trx_id, b.trx_mysql_thread_id blocking_thread, b.trx_query blocking_query FROM information_schema.innodb_lock_waits w INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_trx_id INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_trx_id;
```

<span class="image">![Optional](opt1.png?raw=true)</span>


With Aurora blocking transactions can be monitored through BlockedTransactions and deadlocks through [Deadlocks CW metrics](https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraMySQL.Monitoring.Metrics.html) which might be helpful. You can enable the parameter innodb_print_all_deadlocks to have all deadlocks in InnoDB recorded in mysqld error log.
