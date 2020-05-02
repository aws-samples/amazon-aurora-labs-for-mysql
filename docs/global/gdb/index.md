# Create Global Database from existing Aurora DB cluster

For the sake of time, in the previous CloudFormation scripts, we have automatically launched an Aurora MySQL cluster in the primary region whose version is ready and compatible with Aurora Global Database. We will now create a Global Database which will span across multiple regions.

## Definitions

??? tip "Amazon Aurora Global Database"
    An Amazon Aurora Global Database consists of one primary AWS Region where your data is mastered by the Primary Aurora DB cluster's Primary DB Instance for read and write operations, and one (or more) secondary AWS Region(s) where data is replicated to with typical latency of under a second. Applications with a worldwide footprint can use reader instances in the secondary AWS Region for low latency reads. In the unlikely event your database becomes degraded or isolated in the primary AWS region, you can promote the secondary AWS Region to take full read-write workloads in under a minute.

??? tip "Amazon Aurora DB Cluster"
    An Amazon Aurora DB cluster is a regional logical construct that consists of one or more DB instances and a cluster volume that manages the data for those DB instances.

??? tip "Amazon Aurora Primary DB Instance"
    An Amazon Aurora Primary DB Instance supports read and write operations, and performs all of the data modifications to the cluster volume. Each Aurora DB cluster has one primary DB instance.

??? tip "Amazon Aurora Replica"
    An Amazon Aurora Replica supports only read operations, connects to the same Aurora Storage Engine volume as the Primary DB Instance. High availability can be achieved by locating Aurora Replicas in separate Availability Zones, in which Aurora will automatically perform failover in the event the primary DB Instance becomes unavailable.


## Global Database - Add Region

>  **`Region 1 (Primary)`**

1. Open <a href="https://console.aws.amazon.com/rds" target="_blank">RDS</a> in the AWS Management Console. Ensure you are in your assigned region.

1. Within the RDS console, select **Databases** on the left menu. This will bring you to the list of Databases already deployed. You should see **gdb1-cluster** and **gdb1-node1**.

1. Select **gdb1-cluster**. Click on the **Actions** menu, and select **Add Region**.
    <span class="image">![GDB Add Region](gdb-add-region1.png)</span>

1. You are now creating an Aurora Global Database, adding a new region DB cluster to be replicated from your primary region's Aurora DB cluster.

   1. Under **Global database identifier**. We will name our Global database as ``auroralabs-gdb``

   1. For **Secondary Region**, use the drop down list and select your assigned secondary region **`Region 2 (Secondary)`**. This can take a few seconds to load.

   1. Next, we have **DB Instance Class**. Aurora allows replicas and Global Database instances to be of different instance class and size. We will leave this as the default ``db.r5.large``.
     <span class="image">![GDB Settings 1](gdb-settings1.png)</span>

   1. For **Multi-AZ deployment**, we will leave this as the default value ``Don't create an Aurora Replica``. For production, it is highly recommended to scale your read traffic to multiple reader nodes for even higher availability.

   1. For **Virtual Private Cloud**, we will click on the drop down list, and select ``gdb2-vpc``. This is the dedicated VPC we created from CloudFormation for the secondary region.

   1. Expand on **Additional connectivity configuration** for more options.

   1. Under **Existing VPC security groups**, we will click on the drop down list, <span style="color:red;">deselect</span> ``default`` and <span style="color:green;">select</span> ``gdb2-mysql-internal``. Attaching this security group allows our applications in the secondary region to reach the Aurora secondary DB Cluster.
     <span class="image">![GDB Settings 2](gdb-settings2.png)</span>
      
    !!! warning "Be sure you have the proper VPC selected!" 

   1. Leave the other default options, scroll down to bottom of the page and expand on **Additional configuration**.

   1. For **DB instance identifier**, we will name the Aurora DB instance for the secondary region. Let's name this ``gdb2-node1``

   1. Similarly, under **DB cluster identifier**, we will name the Aurora DB cluster for the secondary region. Let's name this ``gdb2-cluster``

   1. Ensure the **DB cluster parameter group** and **DB parameter groups** are set to the ones with the ``gdb2-`` prefix.
     <span class="image">![GDB Settings 3](gdb-settings3.png)</span>

   1. Near the bottom, under **Monitoring**, select the checkbox for **Enable Enhanced Monitoring**. We will vend metrics down to ``60-second`` **Granularity**. Click on the drop-down menu and change **Monitoring Role** to the IAM role you have under ``gdb2-monitor-<xx-region-x>`` name.
     <span class="image">![GDB Settings 4](gdb-settings4.png)</span>
  
    !!! warning "Please validate and review all settings before moving on" 
        Before moving on, please re-validate all your settings, anything that's not explicitly called out in the instructions here can be left on the default values. Remember, some database settings and configurations are immutable after creation. 
   
   1. After confirming carefully that we have everything in order, press the **Add Region** button.

   1. You will then be returned to the main RDS console and see that the Aurora DB Cluster and DB Instance in your secondary region is being provisioned. This will take about 15-20 minutes and the Secondary DB cluster and new DB instance reader will report as *Available*. You can move on to the next step while this is still being created.
  <span class="image">![GDB Settings 5](gdb-settings5.png)</span>


## Checkpoint

At this point, you have created the Global Database, expanded the Aurora DB cluster from your primary region to replicate data over to the secondary region.

![Global Database Creation Architecture Diagram](gdb-arch.png)
