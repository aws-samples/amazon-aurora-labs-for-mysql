# Monitor Latency

This lab contains the following tasks:

## 4. Use CloudWatch to monitor for latency

https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Monitoring.html

Amazon Aurora vends a variety of Amazon CloudWatch metrics that you can use to monitor and determine the health and performance of your Aurora Global Database. In this lab we will be creating a Amazon CloudWatch Dashboard to monitor for the latency, replicated IO and the cross region replication data transfer for our Aurora Global Database.

There are three different metrics that are applicable to an Aurora Global Database:

CloudWatch Metric Name | Description
----- | -----
``AuroraGlobalDBReplicatedWriteIO`` | The number of Write IO replicated to the secondary region
``AuroraGlobalDBDataTransferBytes`` | The amount of data transferred, in bytes, of redo logs transferred to the secondary region
``AuroraGlobalDBReplicationLag`` | Latency, measured in milliseconds, of the secondary region behind the primary region

#

>  **`Region 2 (Secondary)`** 

1. In the AWS Management Console, ensure that you are working within your assigned secondary region. Using the Service menu, click on or type to search for **CloudWatch**. This will bring up the Amazon CloudWatch console.

1. Within the CloudWatch console, select **Dashboards** on the left menu. Click on the **Create Dashboard** button. Let's name our new dashboard ```aurora-gdb-dashboard``` and click on the **Create Dashboard** button again.

1. Let's add our first widget on the dashboard that will show our replication latency between the secondary and primary Aurora cluster. Select **Number** and then click on **Configure**.
![CloudWatch Dashboard Widgets Creation](cw-widgets.png)

   1. In the **Add Metric Graph** screen, we will look under the **All Metrics** tab, and select **RDS**, and then select the metrics group named **SourceRegion**. 
   
   1. You should now see a filtered Metric Name ```AuroraGlobalDBReplicationLag```, with the SourceRegion column as the name of your Primary Region of the Global Database. Select this metric using the checkbox.
   
   1. The widget preview should now be on top with a sample of the lag time in milliseconds. Let's further update the widget. Give it a friendly name by clicking on the edit icon (pencil icon) and rename the widget from ``Untitled Graph`` to ``GDB Replication Lag Avg (1m)``, press the tick/check icon to submit your changes.
   
   1. On the bottom, let's click on the **Graph Metrics** tab to further customize our view. Under the Statistic column, we want to change this to ``Average`` and Period to ``1 Minute``.

   1. Confirm your settings as similar to that of below, and then click on **Create widget**
   ![CloudWatch AuroraGlobalDBReplicationLag Metric Widget 1](cw-lag-metric1.png)

   1. Now you have created your first widget. You can set this to Auto refresh on a set interval on the top right refresh menu. 
   ![CloudWatch Dashboard Refresh Menu](cw-dash-refresh.png)

   1. To recap, we have added a widget to monitor for the lag time between the Global Database's Primary DB Cluster and Secondary DB Cluster; this metric reports the average of the lag time across 1-minute intervals.
   
   1. Click on the **Save Dashboard** button to save your changes.

1. Next we create a second widget that will show the maximum and average replication latency in a line graph. On the same dashboard, click on the **Add widget** button. This time we select **Line**, and click on **Configure**.

   1. In the **Add Metric Graph** screen, we will look under the **All Metrics** tab, and select **RDS**, and then select the metrics group named **SourceRegion**. 
   
   1. You should now see a filtered Metric Name ```AuroraGlobalDBReplicationLag```, with the SourceRegion column as the name of your Primary Region of the Global Database. Select this metric using the checkbox.
   
   1. The widget preview should now be on top with a sample of the lag time in milliseconds. Let's further update the widget. Give it a friendly name by clicking on the edit icon (pencil icon) and rename the widget from ``Untitled Graph`` to ``GDB Replication Lag Max vs Avg (1m)``, press the tick/check icon to submit your changes.

   1. On the bottom, let's click on the **Graph Metrics** tab to further customize our view. Under the Statistic column, we want to change this to ``Average`` and Period to ``1 Minute``.

   1. On the right column name **Actions**, click on the Copy/Duplicate icon. This adds a new graphed metric for us. On the newly created one, we want to change the Statistic from ``Average`` to ``Maximum``

   1. Confirm your settings as similar to that of below, and then click on **Create widget**
   ![CloudWatch AuroraGlobalDBReplicationLag Metric Widget 2](cw-lag-metric2.png)

   1. Take a moment to understand the metric graph, notice how the average of the ReplicationLag is extremely low, less than 100ms on average. While the Maximum line, representing the worst of replication lag at any given minute; hovers around the 1 second mark. Remember this is replicating the data from your source region to the target region, which can be thousands of kilometers or even continents apart.
   
    1. Click on the **Save Dashboard** button to save your changes.

1. **Extra Challenge:** can you add another widget to display the total of Replicated Write IO and Replicated Data Transfer?

   ![CloudWatch AuroraGlobalDBReplicationLag Metric Widget 3](cw-lag-metric3.png)

## Checkpoint

At this point, you have created a CloudWatch Dashboard, filled with a number of widgets showing graphs of different Aurora Global Database CloudWatch Metrics that are published by the service. You learned how to monitor for latency and lag time of your secondary DB cluster behind the primary DB cluster. With AWS's Global Infrastructure, you can deploy highly available databases for your global audience, while maintaining local low latency expectations. With the combination of CloudWatch and [Amazon SNS (Simple Notification Services)](https://aws.amazon.com/sns/), you can also setup CloudWatch alarms to alert and notify your support engineers and administrators, in the unlikely event your lag time is pegged at a higher threshold for a specific period of time.

![CloudWatch Monitoring Architecture Diagram](cw-arch.png)

Proceed to the next optional step to [Parameter Groups](../pg/index.md).

Proceed to the next step to [Failover](../failover/index.md).