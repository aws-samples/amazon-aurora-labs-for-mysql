# Deploying an Aurora Global Database




This lab contains the following tasks:

1. Create a lab environment in a different region
2. Generate load on your DB cluster
3. Create an Aurora Global cluster
4. Monitor cluster load and replication lag
5. Promote the secondary region
6. Cleanup lab resources

This lab requires the following prerequisites:

* [Get Started](/win/)
* [Connect to your Aurora MySQL DB cluster](/win/ams-connect/)


## 1. Create a lab environment in a different region

To simplify the getting started experience with the labs, we have created foundational templates for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provision the resources needed for the lab environment. These templates are designed to deploy a consistent networking infrastructure, and client-side experience of software packages and components used in the lab.

Click **Launch Stack** below to provision a lab environment in the **N Virginia (us-east-1)** region to support the Aurora Global Database.

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?stackName=labstack&templateURL=https://s3.amazonaws.com/[[bucket]]/templates/lab_template.yml&param_deployCluster=No&param_deployML=No" target="_blank"><img src="/assets/images/cloudformation-launch-stack.png" alt="Launch Stack"></a>

In the field named **Stack Name**, ensure the value `labstack` is preset. Accept all default values for the remaining parameters.

Scroll to the bottom of the page, check the box that reads: **I acknowledge that AWS CloudFormation might create IAM resources with custom names** and then click **Create stack**.

<span class="image">![Create Stack](2-create-stack-confirm.png?raw=true)</span>

The stack will take approximatively 10 minutes to provision, you can monitor the status on the **Stack detail** page. You can monitor the progress of the stack creation process by refreshing the **Events** tab. The latest event in the list will indicate `CREATE_COMPLETE` for the stack resource.

<span class="image">![Stack Status](2-stack-status.png?raw=true)</span>

Once the status of the stack is `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter format: ==[outputKey]==

<span class="image">![Stack Outputs](2-stack-outputs.png?raw=true)</span>


## 2. Generate load on your DB cluster

While the second region is being built up, you will use Percona's TPCC-like benchmark script based on sysbench to generate load on the DB cluster in the existing region. For simplicity we have packaged the correct set of commands in an <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html" target="_blank">AWS Systems Manager Command Document</a>. You will use <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html" target="_blank">AWS Systems Manager Run Command</a> to execute the test. The load generator will run for approximatively one hour.

If you are not already connected to the Session Manager workstation command line, please connect [following these instructions](/win/ams-connect/). Once connected, enter one of the following commands, replacing the placeholders appropriately.

```shell
aws ssm send-command \
--document-name [mysqlRunDoc] \
--instance-ids [bastionMySQL]
```

??? tip "What do all these parameters mean?"
    Parameter | Description
    --- | ---
    --document-name | The name of the command document to run on your behalf.
    --instance-ids | The EC2 instance to execute this command on.

The command will be sent to the workstation EC2 instance which will prepare the test data set and run the load test. It may take up to a minute for CloudWatch to reflect the additional load in the metrics. You will see a confirmation that the command has been initiated.


## 3. Create an Aurora Global cluster

The CloudFormation environment that was provisioned automatically for you, already has an Aurora MySQL DB cluster, that you are running the load generator against. You will create a Global Database cluster using this existing DB cluster, as the **primary**.

???+ info "'Global cluster' vs. 'DB cluster': What is the difference?"
    A **DB cluster** exists in one region only. It is a container for up to 16 **DB instances** that share the same storage volume. This is the traditional configuration of an Aurora cluster. Whether you are deploying a provisioned, Serverless or Multi-Master cluster, you are deploying a **DB cluster**, within a single region.

    A **Global [database] cluster** is a container for several **DB clusters** each located in a different region, that act as a cohesive database. A **global cluster** is comprised of a **primary [DB] cluster** in one given region that is able to accept writes, and up to 5 **secondary [DB] clusters** that are read-only each in a different region. Each one of the **DB clusters** in a given **global cluster** have their own storage volume, however data is replicated from the **primary cluster** to each of the **secondary clusters** asynchronously, using a purpose-built low latency and high throughput replication system.  

Once the lab environment created above at **Step 1. Create a lab environment in a different region** has finished deploying, you may proceed.

Open the <a href="https://eu-west-1.console.aws.amazon.com/rds/home?region=eu-west-1#database:id=labstack-mysql-cluster;is-cluster=true" target="_blank">Amazon RDS service console</a> at the MySQL DB cluster details page. If you navigated to the RDS console by means other than the link in this paragraph, click on the `labstack-mysql-cluster` in the **Databases** section of the RDS service console.

From the **Actions** dropdown button, choose **Add region**.

::TODO:: screenshot

On the setup screen, under **Global database settings**, set the **Global database identifier** to `labstack-mysql-global`. Under **Region**, choose the **Secondary region** of `US East (N. Virginia)`.

In the **Connectivity** section, expand the sub-section called **Additional connectivity configuration**. This section allows you to specify where the database cluster will be deployed within your defined network configuration created above.

Pick the **Virtual Private Cloud (VPC)** named `labstack-vpc`. Similarly make sure the selected **Subnet Group** also matches the stack name (e.g. `labstack-dbsubnets-[hash]`). Make sure the cluster **Publicly accessible** option is set to **No**. The lab environment also configured a **VPC security group** that allows your lab workspace EC2 instance to connect to the database. Make sure the **Choose existing** security group option is selected and from the dropdown pick the security group named `labstack-mysql-internal`. Please remove any other security groups, such as `default` from the selection.

::TODO:: screenshot

Next, expand the **Advanced configuration** section. Set the **DB instance identifier** to `labstack-mysql-node-3` and the **DB cluster identifier** to `labstack-mysql-secondary`. For the **DB cluster parameter group** and **DB parameter group** selectors, choose the groups with the stack name in their name (e.g. `labstack-[...]`).

Keep the `1 day` **Backup retention period**. Check the box to **Enable Performance Insights** with a **Retention period of `Default (7 days)` and use the `[default] aws/rds` **Master key** for monitoring data encryption. Next, check the **Enable Enhanced Monitoring** box, and select a **Granularity** of `1 second`.

::TODO:: screenshot

??? tip "What do these selections mean?"
    You will create a global cluster, a secondary DB cluster, and DB instance in that secondary cluster, with associated configurations in one step. Your existing DB cluster will become the primary DB cluster in the new global cluster. These are distinct API calls to the RDS service should you create a global cluster using the AWS CLI, SDKs or other tools. The RDS service console, simply combines these distinct steps into a single operation.

Click **Add region** to provision the global cluster.

!!! note
    Creating a global cluster based on the existing DB cluster is a seamless operation, your workload will not experience any disruption. You can monitor the performance metrics of the load generator started above, throughout this operation to validate.

The global cluster, including the secondary DB cluster and instance may take several minutes to provisions. In order to connect to the DB cluster and start using it , you need to retrieve the DB cluster endpoints. Unlike a regular DB cluster, only the **Reader Endpoint** is provisioned. The **Cluster Endpoint** is not being provisioned, as secondary DB clusters only contain readers, and cannot accept writes. The **Reader Endpoint** will always resolve to one of the reader DB instances and should be used for low latency read operations within that region. In the RDS console, go to the DB cluster detail view by clicking on the cluster DB identifier.

::TODO:: screenshot

The **Endpoints** section in the **Connectivity and security** tab of the details page displays the endpoints. Note these values down, as you will use them later.

::TODO:: screenshot


## 4. Monitor cluster load and replication lag

Since the new **primary DB cluster** was in-use before you created the Global cluster using it, you can review the performance metrics of the cluster. In the RDS service console, select the `labstack-mysql-cluster` (primary), if it is not already selected and toggle to the **Monitoring** tab. You will see a combined view of both the writer and reader DB instances in that cluster. You are not using the reader at this time, the load is directed only to the writer. Navigate through the metrics, and specifically review the **CPU Utilization**, **Commit Throughput**, **DML Throughput**, **Select Throughput** metrics, and notice they are fairly stable, beyond the initial spike caused by the sysbench tool populating an initial data set.

::TODO:: screenshot

Next you will shift focus to the newly created **secondary DB cluster**. You will create a CloudWatch Dashboard to monitor three key metrics relevant to global clusters, and secondary DB clusters more specifically:

CloudWatch Metric Name | Description
----- | -----
`AuroraGlobalDBReplicatedWriteIO` | The number of Write IO replicated to the secondary region
`AuroraGlobalDBDataTransferBytes` | The amount of redo logs transferred to the secondary region, in bytes
`AuroraGlobalDBReplicationLag` | How far behind, measured in milliseconds, the secondary region lags behind the writer in the primary region

!!! warning "Region Check"
    You are going to work in a different region in the subsequent steps: N. Virginia (us-east-1). As you have multiple browser tabs and command line sessions open, please make sure you are always operating in the intended region.

Open the <a href="https://console.aws.amazon.com/cloudwatch" target="_blank">Amazon CloudWatch service console</a> in the secondary region.

::TODO:: screenshot

Select **Dashboards** on the left menu. Click **Create Dashboard**. Let's name our new dashboard ```aurora-gdb-dashboard``` and click on the **Create Dashboard** button again.

Let's add our first widget on the dashboard that will show our replication latency between the secondary and primary Aurora cluster. Select **Number** and then click on **Configure**.

<span class="image">![CloudWatch Dashboard Widgets Creation](cw-widgets.png)</span>

In the **Add Metric Graph** screen, we will look under the **All Metrics** tab, and select **RDS**, and then select the metrics group named **SourceRegion**.

You should now see a filtered Metric Name `AuroraGlobalDBReplicationLag`, with the SourceRegion column as the name of your primary region of the global cluster. Select this metric using the checkbox.

The widget preview should now be on top with a sample of the lag time in milliseconds. Let's further update the widget. Give it a friendly name by clicking on the edit icon (pencil icon) and rename the widget from `Untitled Graph to `Global DB Replication Lag Avg (1m)`, press the tick/check icon to submit your changes.

On the bottom, click on the **Graph Metrics** tab to further customize our view. Under the **Statistic** column, we want to change this to `Average` and **Period** to `1 Minute`.

Confirm your settings are similar to the example below, and then click **Create widget**.

<span class="image">![CloudWatch AuroraGlobalDBReplicationLag Metric Widget 1](cw-lag-metric1.png)</span>

Now you have created your first widget. You can set this to Auto refresh on a set interval on the top right refresh menu.

<span class="image">![CloudWatch Dashboard Refresh Menu](cw-dash-refresh.png)</span>

Click **Save Dashboard** to save your changes.

Next, create a second widget that will show the maximum and average replication latency in a line graph. On the same dashboard, click on the **Add widget** button. This time we select **Line**, and click on **Configure**.

In the **Add Metric Graph** screen, look under the **All Metrics** tab, and select **RDS**, and then select the metrics group named **SourceRegion**.

You should now see a filtered Metric Name `AuroraGlobalDBReplicationLag`, with the SourceRegion column as the name of your primary region of the global cluster. Select this metric using the checkbox.

The widget preview should now be on top with a sample of the lag time in milliseconds. Let's further update the widget. Give it a friendly name by clicking on the edit icon (pencil icon) and rename the widget from `Untitled Graph` to `Global DB Replication Lag Max vs. Avg (1m)`, press the tick/check icon to submit your changes.

On the bottom, click on the **Graph Metrics** tab to further customize our view. Under the **Statistic** column, we want to change this to `Average` and **Period** to `1 Minute`.

On the right column name **Actions**, click on the Copy/Duplicate icon. This adds a new graphed metric for us. On the newly created one, we want to change the Statistic from `Average` to `Maximum`

Confirm your settings are similar to the example below, and then click **Create widget**.

<span class="image">![CloudWatch AuroraGlobalDBReplicationLag Metric Widget 2](cw-lag-metric2.png)</span>

Take a moment to understand the metric graph, notice how the average of the ReplicationLag is extremely low, less than 100ms on average. While the Maximum line, representing the worst of replication lag at any given minute hovers around the 1 second mark. Remember this is replicating the data from your source region to the target region, which can be thousands of kilometers or even continents apart.

Click **Save Dashboard** to save your changes.

**Extra Challenge:** can you add another widget to display the total of Replicated Write IO and Replicated Data Transfer?

<span class="image">![CloudWatch AuroraGlobalDBReplicationLag Metric Widget 3](cw-lag-metric3.png)</span>

## 5. Promote the secondary region


## 6. Cleanup lab resources
