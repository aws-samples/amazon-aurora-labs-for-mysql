Graviton2 vs x86 Comparison

This lab will compare the performance between between X86 instance and Graviton2 based r6g instance class.

This lab contains the following tasks:


1. Add a new x86 based r5.large Aurora replica
2. Simulate an OLTP workload with sysbench, using the Graviton r6g.large instance.
3. Promote the x86 based r6g.large Aurora replica to become the primary.
4. Repeat simulated OLTP workload using sysbench, using the r5.large primary instance.
5. Compare results.
6. Cleanup lab resources

This lab requires the following prerequisties:

* [Get Started](/prereqs/environment/)
* [Connect to the Cloud9 Desktop](/prereqs/connect/)
* [Create a New DB Cluster](/provisioned/create/) (conditional, only if you plan to create a cluster manually)

## 1. Add a new x86 based r5.large Aurora replica.

The lab environment that was provisioned automatically for you, already has an Aurora MySQL DB cluster with 2 instances (`1 Writer and 1 Reader`) running on r6g.large (Graviton2) instance class.

Open the <a href="https://console.aws.amazon.com/rds/home#databases:" target="_blank">Amazon RDS Service console</a>, if you don’t already have it open. Click the radio button for the Aurora cluster “auroralab-mysql-cluster” and click *Actions* then click *Add reader*

<span class="image">![Add Reader](add-x86-reader-instance.png?raw=true)</span>

Provide `auroralab-mysql-x86-node-3` as the DB instance identifier and select `db.r5.large` **x86** instance class in the Instance configuration section.

<span class="image">![x86 instance config](x86-instance-config.png?raw=true)</span>

Set failover priority tier to `tier-0` to ensure that this instance is available as a failover target. Leave rest of the configurations to default.

<span class="image">![Set instance priority](x86-instance-failover-priority.png?raw=true)</span>

Click on **Add reader** button to x86 Aurora reader instance.

<span class="image">![Add Reader](x86-instance-click-add-reader.png?raw=true)</span>


## 2. Simulate an OLTP workload with sysbench in r6g.large (Graviton2) instance.

If you have not already opened a terminal window in the Cloud9 desktop in a previous lab, please following these instructions(##add hyperlink) to do so now. Once connected, run the command below to create database to test the workload.

```
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS"
create database graviton_test;
quit;
```
In the `Cloud9 desktop` run the following command to populate the tables with sample data. It will take approximately *10 minutes* to finish populating the data to the tables. Replace `[Cluster-endpoint]` with your cluster end-point.

```
sysbench /usr/share/sysbench/oltp_read_write.lua --mysql-host=[Cluster-endpoint] --mysql-user=$DBUSER --mysql-password=$DBPASS --mysql-db=graviton_test --threads=16 --tables=25 --table-size=1000000 prepare
```
<span class="image">![Add Reader](sysbench_prepare_data.png?raw=true)</span>

Once sysbench successfully populated the data. We can start the load test, run the following command to start the load test on x86  instance. Replace `[Cluster-endpoint]` with your cluster end-point.

```
sysbench /usr/share/sysbench/oltp_read_write.lua --mysql-host=[Cluster-endpoint] --mysql-user=$DBUSER --mysql-password=$DBPASS --mysql-db=graviton_test --time=600 --threads=16 --tables=25 --table-size=1000000 --report-interval=1 run
```
The above workload will run for **10 minutes**. After letting this test run for ~5 minutes, observe the CloudWatch metrics for *“auroralab-mysql-node-2”* instance by clicking on the *DB identifier* and going to the *Monitoring tab*.

<span class="image">![Add Reader](Graviton2_metrics_monitoring.png?raw=true)</span>

After reviewing the metrics, navigate to RDS Performance Insights in the RDS console. Select “auroralab-mysql-node-2” in the drop down menu, and click on *Manage Metrics.*

<span class="image">![Add Reader](Graviton2_PI_manage_metrics.png?raw=true)</span>

Select “*Database metrics*” and select the following options under *SQL* and *Transactions* sections.

* Innodb_rows_inserted
* Innodb_rows_updated
* Innodb_rows_read
* active_transactions

<span class="image">![Add Reader](Graviton2_PI_metrics_selection.png?raw=true)</span>

Once the sysbench workload completes, you should see results similar to the following in RDS Performance Insights.

<span class="image">![Add Reader](Graviton2_PI_metrics.png?raw=true)</span>

<span class="image">![Add Reader](Graviton2_PI_DBLoad.png?raw=true)</span>

<span class="image">![Add Reader](Graviton2_PI_TopSQL.png?raw=true)</span>

After reviewing the Performance Insights metrics. Copy the results of the sysbench SQL statistics from Cloud9 terminal to notepad, we will use it to compare the results at the end of this lab.

## 3. Promote x86 based r5.large Aurora replica to become the primary instance.

Now, lets failover to x86 based r5.large Aurora MySQL instance. Select any instance of the Aurora cluster “auroralab-mysql-cluster” and then select *Failover* in the *Actions* menu.

<span class="image">![Add Reader](Graviton2_to_x86_failover.png?raw=true)</span>
Confirm the failover action on the next screen.
<span class="image">![Add Reader](x86-confirm-failover.png?raw=true)</span>
Wait for ~30 seconds and refresh your browser window to verify that the auroralab-mysql-x86-node-3 instance has become the new Writer instance.
<span class="image">![Add Reader](x86_writer_instance.png?raw=true)</span>
We are going to simulate the same OLTP workload in x86 instance.

## 4. Repeat simulated OLTP workload using sysbench in r5.large instance.

Run the sample OLTP workload by running the following command in your Cloud9 environment. Replace `[Cluster-endpoint]` with your cluster end-point.

```
sysbench /usr/share/sysbench/oltp_read_write.lua --mysql-host=[Cluster-endpoint] --mysql-user=$DBUSER --mysql-password=$DBPASS --mysql-db=graviton_test --time=600 --threads=16 --tables=25 --table-size=1000000 --report-interval=1 run
```
The above workload will run for 10 minutes. After letting this test run for **~5 minutes**, observe the CloudWatch metrics for current Graviton2 writer instance by clicking on the **DB identifier** and going to the **Monitoring tab**.

<span class="image">![Add Reader](x86_metrics_monitoring.png?raw=true)</span>

After reviewing the metrics, navigate to  <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html" target="_blank"> RDS Performance Insights </a> in the RDS console. Select Graviton2 writer instance in the drop down menu.

<span class="image">![Add Reader](x86_PI_Counter_metrics.png?raw=true)</span>

<span class="image">![Add Reader](x86_PI_DBLoad.png?raw=true)</span>

<span class="image">![Add Reader](x86_PI_TopSQL.png?raw=true)</span>

We have ran sample workload in both Graviton2 and x86 instance class. In the next section, we will compare the results.

## 5.Compare results

Let's compare our sample OLTP workload results agains x86 based db.r5.large and Graviton2 based r6g.large database instances.

*SQL Statistics for Simulated Online Transaction Processing (OLTP) Workload using sysbench*

#### **Results from Graviton2 based instance**

Results from Performance Insights metrics

<span class="image">![Grav2 PI](Graviton2_PI_counter_results.png?raw=true)</span>

SQL Statistics results from Sysbench
<span class="image">![Graviton SQL stats](Graviton2_SQL_statistics.png?raw=true)</span>

#### **Results from x86 based instance**

Results from Performance Insights metrics
<span class="image">![X86 PI](x86_PI_counter_results.png?raw=true)</span>

SQL Statistics results from Sysbench

<span class="image">![Add Reader](x86_SQL_statistics.png?raw=true)</span>

Lets compare the results:


|                     Stats                      | x86 based db.r5.large | Graviton2 based db.r6g.large | Performance difference |
|------------------------------------------------|-----------------------|------------------------------|------------------------|
| Average rows read per second                   |                140711 |                       206659 | 37%                    |
| Average rows inserted per second               |                   340 |                          500 | 38%                    |
| Average rows updates per second                |                   681 |                         1000 | 41%                    |
| Average sysbench Transactions Per Second (TPS) |                   314 |                          492 | 44%                    |



#### **Price Comparison**
Taking these metrics into consideration, lets examine the cost efficiency of the tested instances for the given sample workload.


| Instance Type |    Specifications     | Hourly Rate** | Avg sysbench TPS |
|---------------|-----------------------|---------------|------------------|
| db.r5.large   | 2 vCPU & 16GB Memory  | $0.29         |              314 |
| db.r6g.large  | 2 vCPU & 16 GB Memory | $0.26         |              492 |



Based on the above comparison Graviton2 instance is 10% cheaper with 33% more TPS.

*Cost based on Provisioned on-demand instance <a href="https://aws.amazon.com/rds/aurora/pricing/" target="_blank"> cost </a> of Aurora MySQL  in us-west-2 AWS region*

#### **Conclusion:**

*Were your results similar to those presented here?*

Each workload is a little different, and using data and a repeatable methodology is key to evaluating which processor architecture will achieve the best results for a given workload. As you saw here, choosing the best Aurora PostgreSQL instance type for your workloads can enable meaningful cost savings with increased performance.


## 6. Cleanup lab resources

By running this lab, you have created additional AWS resources. We recommend you run the commands below to remove these resources once you have completed this lab, to ensure you do not incur any unwanted charges for using these services.

```
aws rds delete-db-instance --db-instance-identifier auroralab-mysql-x86-node-3
```
