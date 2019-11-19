# Using Performance Insights

This lab will demonstrate the use of <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_PerfInsights.html" target="_blank">Amazon RDS Performance Insights</a>. Amazon RDS Performance Insights monitors your Amazon RDS DB instance load so that you can analyze and troubleshoot your database performance.

This lab contains the following tasks:

1. Generating load on your DB cluster
2. Understanding the Performance Insights interface
3. Examining the performance of your DB instance

This lab requires the following lab modules to be completed first:

* [Prerequisites](/reinvent/prerequisites/)
* [Connecting, Loading Data and Auto Scaling](/reinvent/connect/) (connectivity section only)


## 1. Generating load on your DB cluster

You will use Percona's TPCC-like benchmark script based on sysbench to generate load. For simplicity we have packaged the correct set of commands in an <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html" target="_blank">AWS Systems Manager Command Document</a>. You will use <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html" target="_blank">AWS Systems Manager Run Command</a> to execute the test.

On the Session Manager workstation command line [see the Connecting, Loading Data and Auto Scaling lab](/reinvent/connect/#1-connecting-to-your-workstation-ec2-instance), enter following command.

```
aws ssm send-command \
--document-name [loadTestRunDoc] \
--instance-ids [bastionInstance]
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value | Description
--- | --- | --- | ---
--document-name | [loadTestRunDoc] | See CloudFormation stack output | The name of the command document to run on your behalf.
--instance-ids | [bastionInstance] | See CloudFormation stack output | The EC2 instance to execute this command on.

The command will be sent to the workstation EC2 instance which will prepare the test data set and run the load test. It may take up to a minute for CloudWatch to reflect the additional load in the metrics. You will see a confirmation that the command has been initiated.

<span class="image">![SSM Command](../../modules/perf-insights/1-ssm-command.png?raw=true)</span>


## 2. Understanding the Performance Insights interface

While the command is running, open the <a href="https://eu-west-1.console.aws.amazon.com/rds/home?region=eu-west-1" target="_blank">Amazon RDS service console</a> in a new tab, if not already open.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

In the menu on the left hand side, click on the **Performance Insights** menu option.

<span class="image">![RDS Dashboard](../../modules/perf-insights/2-menu-perf-ins.png?raw=true)</span>

Next, select the desired **DB instance** to load the performance metrics for. For Aurora DB clusters, performance metrics are exposed on an individual DB instance basis. As the different Db instances comprising a cluster may run different workload patterns, and might not all have Performance Insights enabled. For this lab we are generating load on the **Writer** (master) DB instance only. Select the DB instance where the name ends in `-node-01`.

<span class="image">![Select DB Instance](../../modules/perf-insights/2-select-instance.png?raw=true)</span>

Once a DB instance is selected, you will see the main dashboard view of RDS Performance Insights. The dashboard is divided into 3 sections, allowing you to drill down from high level performance indicator metrics down to individual queries, waits, users and hosts generating the load.

<span class="image">![Performance Insights Dashboard](../../modules/perf-insights/2-pi-dashboard.png?raw=true)</span>

The performance metrics displayed by the dashboard are a moving time window. You can adjust the size of the time window by clicking the buttons across the top right of the interface (`5m`, `1h`, `5h`, `24h`, `1w`, `all`). You can also zoom into a specific period of time by dragging across the graphs.

!!! note
    All dashboard views are time synchronized. Zooming in will adjust all views, including the detailed drill-down section at the bottom.

Section | Filters | Description
--- | --- | ---
**Counter Metrics** | Click cog icon in top right corner to select additional counters | This section plots internal database counter metrics over time, such as number of rows read or written, buffer pool hit ratio, etc. These counters are useful to correlate with other metrics, including the database load metrics, to identify causes of abnormal behavior.
**Database load** | Load can be sliced by waits (default), SQL commands, users and hosts | This metric is design to correlate aggregate load (sliced by the selected dimension) with the available compute capacity on that DB instance (number of vCPUs). Load is aggregated and normalized using the **Average Active Session** (AAS) metric. A number of AAS that exceeds the compute capacity of the DB instance is a leading indicator of performance problems.
Granular Session Activity | Sort by **Waits**, **SQL** (default), **Users** and **Hosts** | Drill down capability that allows you to get detailed performance data down to the individual commands.


## 3. Examining the performance of your DB instance

After running the load generator workload above, you will see a performance profile similar to the example below in the Performance Insights dashboard. The load generator command will first create an initial data set using `sysbench prepare`. And then will run an OLTP workload for the duration of 5 minutes, consisting of concurrent transactional reads and writes using 4 parallel threads.

<span class="image">![Load Test Profile](../../modules/perf-insights/3-load-profile.png?raw=true)</span>

Amazon Aurora MySQL specific wait events are documented in the <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Reference.html#AuroraMySQL.Reference.Waitevents" target="_blank">Amazon Aurora MySQL Reference guide</a>. Use the Performance Insights dashboard and the reference guide documentation to evaluate the workload profile of your load test, and answer the following questions:

1. Is the database server overloaded at any point during the load test?
2. Can you identify any resource bottlenecks during the load test? If so how can they be mitigated?
3. What are the most common wait events during the load test?
4. Why are the load patterns different between the first and second phase of the load test?
