# Monitor a Global Database

::TODO:: adjust from here on down

Amazon Aurora exposes a variety of <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Monitoring.html" target="_blank">Amazon CloudWatch metrics</a>, that you can use to monitor and determine the health and performance of your Aurora Global Database. In this lab you will create a Amazon CloudWatch Dashboard to monitor for the latency, replicated IO and the cross region replication data transfer for our Aurora Global Database.

This lab contains the following tasks:

1. Generate load on the primary DB cluster
2. Monitor cluster load and replication lag

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/) (choose the **Deploy Global DB** option)
* [Connect to the Session Manager Workstation](/prereqs/connect/)
* [Deploy an Aurora Global Database](/global/deploy/)


## 1. Generate load on the primary DB cluster

You will use Percona's TPCC-like benchmark script based on sysbench to generate load. For simplicity we have packaged the correct set of commands in an <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html" target="_blank">AWS Systems Manager Command Document</a>. You will use <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html" target="_blank">AWS Systems Manager Run Command</a> to execute the test.

If you are not already connected to the Session Manager workstation command line, please connect [following these instructions](/prereqs/connect/) in the **primary region**. Once connected, enter one of the following commands, replacing the placeholders appropriately.

!!! warning "Region Check"
    Ensure you are still working in the **primary region**, especially if you are the links in this guide to open the service console at the right screen.

If you have completed the [Create a New DB Cluster](/provisioned/create/) lab, and created the Aurora DB cluster manually execute this command:

```shell
aws ssm send-command \
--document-name [loadTestRunDoc] \
--instance-ids [ec2Instance] \
--parameters \
clusterEndpoint=[clusterEndpoint],\
dbUser=$DBUSER,\
dbPassword="$DBPASS"
```

If AWS CloudFormation has provisioned the DB cluster on your behalf, and you skipped the **Create a New DB Cluster** lab, you can run this simplified command:

```shell
aws ssm send-command \
--document-name [loadTestRunDoc] \
--instance-ids [ec2Instance]
```

??? tip "What do all these parameters mean?"
    Parameter | Description
    --- | ---
    --document-name | The name of the command document to run on your behalf.
    --instance-ids | The EC2 instance to execute this command on.
    --parameters | Additional command parameters.

The command will be sent to the workstation EC2 instance which will prepare the test data set and run the load test. It may take up to a minute for CloudWatch to reflect the additional load in the metrics. You will see a confirmation that the command has been initiated.

<span class="image">![SSM Command](ssm-cmd-sysbench.png?raw=true)</span>


## 2. Monitor cluster load and replication lag

In the RDS service console in the **primary region**, select the `auroralab-mysql-cluster` (primary), if it is not already selected and toggle to the **Monitoring** tab. You will see a combined view of both the writer and reader DB instances in that cluster. You are not using the reader at this time, the load is directed only to the writer. Navigate through the metrics, and specifically review the **CPU Utilization**, **Commit Throughput**, **DML Throughput**, **Select Throughput** metrics, and notice they are fairly stable, beyond the initial spike caused by the sysbench tool populating an initial data set.

<span class="image">![RDS Cluster Primary Metrics](rds-cluster-primary-metrics.png?raw=true)</span>

Next you will shift focus to the newly created **secondary DB cluster**. You will create a CloudWatch Dashboard to monitor three key metrics relevant to global clusters, and secondary DB clusters more specifically:

CloudWatch Metric Name | Description
----- | -----
`AuroraGlobalDBReplicatedWriteIO` | The number of Write IO replicated to the secondary region
`AuroraGlobalDBDataTransferBytes` | The amount of redo logs transferred to the secondary region, in bytes
`AuroraGlobalDBReplicationLag` | How far behind, measured in milliseconds, the secondary region lags behind the writer in the primary region

Open the <a href="https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:" target="_blank">Amazon CloudWatch service console</a> in the secondary region at the **Dashboards** feature.

!!! warning "Region Check"
    You are going to work in a different region in the subsequent steps: N. Virginia (us-east-1). As you have multiple browser tabs and command line sessions open, please make sure you are always operating in the intended region.

<span class="image">![CloudWatch Dashboards Listing](cw-dash-listing.png?raw=true)</span>

Click **Create dashboard**. Let's name our new dashboard `auroralab-gdb-dashboard` and click on the **Create dashboard** button again.

<span class="image">![CloudWatch Dashboard Creation](cw-dash-create.png)</span>

Let's add our first widget on the dashboard that will show our replication latency between the secondary and primary Aurora cluster. Select **Number** and then click on **Configure**.

<span class="image">![CloudWatch Dashboard Add Number Widget](cw-dash-add-number.png)</span>

In the **Add Metric Graph** screen, we will look under the **All Metrics** tab, and select **RDS**, and then select the metrics group named **SourceRegion**.

You should now see a filtered Metric Name `AuroraGlobalDBReplicationLag`, with the SourceRegion column as the name of your primary region of the global cluster. Select this metric using the checkbox.

The widget preview should now be on top with a sample of the lag time in milliseconds. Let's further update the widget. Give it a friendly name by clicking on the edit icon (pencil icon) and rename the widget from `Untitled Graph` to `Global DB Replication Lag (avg, 1min)`, press the tick/check icon to submit your changes.

On the bottom, click on the **Graph Metrics** tab to further customize our view. Under the **Statistic** column, we want to change this to `Average` and **Period** to `1 Minute`.

Confirm your settings are similar to the example below, and then click **Create widget**.

<span class="image">![CloudWatch Widget Configuration](cw-widget-setup.png)</span>

Now you have created your first widget. You can set this to Auto refresh on a set interval on the top right refresh menu.

Click **Save dashboard** to save your changes.

<span class="image">![CloudWatch Dashboard Single Widget](cw-dash-single-widget.png)</span>

You can add widgets individually to the dashboard, to build a more complete monitoring dashboard. However, to save some time you will simply update the source of the dashboard with the below JSON specification.

First, click the **Actions** dropdown on the dashboard, and choose **View/edit source**.

<span class="image">![CloudWatch Dashboard Actions](cw-dash-actions.png)</span>

In the textbox that appears on the screen, paste the following JSON code. Be sure to update the correct AWS regions, corresponding to your primary and secondary DB clusters, if needed in the code below. Also, if you used different DB cluster identifiers (names) for the DB clusters than the ones indicated in this guide, you will have to update those as well.

```json
{
    "widgets": [
        {
            "type": "metric",
            "x": 0,
            "y": 3,
            "width": 24,
            "height": 6,
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "AuroraGlobalDBReplicationLag", "DBClusterIdentifier", "auroralab-mysql-secondary" ],
                    [ "...", { "stat": "Maximum" } ]
                ],
                "view": "timeSeries",
                "stacked": false,
                "region": "us-east-1",
                "title": "Global DB Replication Lag (max vs. avg, 1min)",
                "stat": "Average",
                "period": 60
            }
        },
        {
            "type": "metric",
            "x": 0,
            "y": 0,
            "width": 9,
            "height": 3,
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "AuroraGlobalDBReplicationLag", "DBClusterIdentifier", "auroralab-mysql-secondary" ]
                ],
                "view": "singleValue",
                "region": "us-east-1",
                "title": "Global DB Replication Lag (avg, 1min)",
                "stat": "Average",
                "period": 60
            }
        },
        {
            "type": "metric",
            "x": 9,
            "y": 0,
            "width": 15,
            "height": 3,
            "properties": {
                "metrics": [
                    [ "AWS/RDS", "AuroraGlobalDBReplicatedWriteIO", "DBClusterIdentifier", "auroralab-mysql-secondary", { "label": "Global DB Replicated Write IOs" } ],
                    [ ".", "AuroraGlobalDBDataTransferBytes", ".", ".", { "label": "Global DB DataTransfer Bytes" } ]
                ],
                "view": "singleValue",
                "region": "us-east-1",
                "stat": "Sum",
                "period": 86400,
                "title": "Billable Replication Metrics (aggregate, last 24 hr)"
            }
        }
    ]
}
```

Click **Update** to change the dashboard.

<span class="image">![CloudWatch Dashboard Source](cw-dash-source.png)</span>

Click **Save dashboard** to make sure the dashboard is saved with the new changes.

<span class="image">![CloudWatch Dashboard Multiple Widgets](cw-dash-multi-widget.png)</span>

!!! note
    The **Aurora Global DB Replicated I/O** and **Aurora Global DB Data Transfer Bytes** metrics are only reported once an hour, so you may not be able to see any data for those metrics depending on the timing of your lab. If you are doing other labs, please continue with those labs, and come back later to check these metrics.
