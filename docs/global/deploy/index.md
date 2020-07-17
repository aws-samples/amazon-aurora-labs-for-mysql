# Deploy an Aurora Global Database

Amazon Aurora <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html" target="_blank">Global Database</a> is designed for globally distributed applications, allowing a single Amazon Aurora database to span multiple AWS regions. It replicates your data with no impact on database performance, enables fast local reads with low latency in each region, and provides disaster recovery from region-wide outages.

This lab contains the following tasks:

1. Create a lab environment in a different region
2. Create an Aurora global cluster

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/) (choose the **Deploy Global DB** option)
* [Create a New DB Cluster](/provisioned/create/) (conditional, only if you plan to create a cluster manually)


## 1. Create a lab environment in a different region

!!! warning "Using Multiple Regions"
    Due to the **multi-region** nature of a Global Database, you will often be switching between two regions to accomplish the tasks in this lab. **Please be mindful** that you are performing the actions in the proper region, as some of the resources created are very similar between the two regions.

    We will refer to the region where your current DB cluster is deployed, and you have been working in so far, as your **primary region**. 

    We will refer to the region where you will deploy the secondary, read-only DB cluster as the **secondary region**.

To simplify the getting started experience with the labs, we have created foundational templates for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provision the resources needed for the lab environment. These templates are designed to deploy a consistent networking infrastructure, and client-side experience of software packages and components used in the lab.

Click **Launch Stack** below to provision a lab environment in the **US East (N Virginia, us-east-1)** region to support the Aurora Global Database.

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?stackName=auroralab&templateURL=https://s3.amazonaws.com/[[bucket]]/templates/lab_template.yml&param_deployCluster=No&param_deployML=No&param_deployGDB=Yes&param_isSecondary=Yes" target="_blank"><img src="/assets/images/cloudformation-launch-stack.png" alt="Launch Stack"></a>

In the field named **Stack Name**, ensure the value `auroralab` is preset. Accept all default values for the remaining parameters.

Scroll to the bottom of the page, check the box that reads: **I acknowledge that AWS CloudFormation might create IAM resources with custom names** and then click **Create stack**.

<span class="image">![Create Stack](cfn-create-stack-confirm.png?raw=true)</span>

The stack will take approximatively 10 minutes to provision, you can monitor the status on the **Stack detail** page. You can monitor the progress of the stack creation process by refreshing the **Events** tab. The latest event in the list will indicate `CREATE_COMPLETE` for the stack resource.

<span class="image">![Stack Status](cfn-stack-status.png?raw=true)</span>

Once the status of the stack is `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter format: ==[outputKey]==.

<span class="image">![Stack Outputs](cfn-stack-outputs.png?raw=true)</span>


## 2. Create an Aurora global cluster

The lab environment that was provisioned automatically for you, already has an Aurora MySQL DB cluster, that you are running the load generator against. You will create a Global Database cluster using this existing DB cluster, as the **primary**.

???+ info "'Global cluster' vs. 'DB cluster': What is the difference?"
    A **DB cluster** exists in one region only. It is a container for up to 16 **DB instances** that share the same storage volume. This is the traditional configuration of an Aurora cluster. Whether you are deploying a provisioned, Serverless or Multi-Master cluster, you are deploying a **DB cluster**, within a single region.

    A **Global [database] cluster** is a container for several **DB clusters** each located in a different region, that act as a cohesive database. A **global cluster** is comprised of a **primary [DB] cluster** in one given region that is able to accept writes, and up to 5 **secondary [DB] clusters** that are read-only each in a different region. Each one of the **DB clusters** in a given **global cluster** have their own storage volume, however data is replicated from the **primary cluster** to each of the **secondary clusters** asynchronously, using a purpose-built low latency and high throughput replication system.  

Once the lab environment created above at **Step 1. Create a lab environment in a different region** has finished deploying, you may proceed.

Open the <a href="https://console.aws.amazon.com/rds/home#database:id=auroralab-mysql-cluster;is-cluster=true" target="_blank">Amazon RDS service console</a> at the MySQL DB cluster details page in the **primary** region. If you navigated to the RDS console by means other than the link in this paragraph, click on the `auroralab-mysql-cluster` in the **Databases** section of the RDS service console, and make sure you are back in the primary regions.

!!! warning "Region Check"
    Ensure you are still working in the **primary region**, especially if you are following the links above to open the service console at the right screen.

First, you need to **disable** the **Backtrack** feature. At present database backtrack is not compatible with Aurora Global Databases, and a cluster with that feature active cannot be converted into a global database. Select the `auroralab-mysql-cluster` and click the **Modify** button.

!!! note
    If you have not completed the [Backtrack a DB Cluster](/provisioned/backtrack/) lab already, and wish to do so, or have been instructed to do so part of the event, please complete that lab now before moving forward. Once disabled, you will not be able to re-enable the backtrack feature on an existing DB cluster.

<span class="image">![RDS Cluster Modify](rds-cluster-action-modify.png?raw=true)</span>

Scroll down to the **Backtrack** section and choose the **Disable Backtrack** option, then click **Continue** at the bottom of the page.

<span class="image">![RDS Cluster Disable Backtrack](rds-cluster-disable-backtrack.png?raw=true)</span>

In the **Scheduling of modifications** section, choose the **Apply immediately** option, then click **Modify cluster** to confirm the changes.

<span class="image">![RDS Cluster Confirm Changes](rds-cluster-modify-confirm.png?raw=true)</span>

Once the modification is complete, and the DB cluster is in an `available` state again, from the **Actions** dropdown button, choose **Add region**.

<span class="image">![RDS Cluster Add Region](rds-cluster-action-add.png?raw=true)</span>

Set the following options on the configuration screen for the secondary DB cluster:

1. In the **Global database settings** section:
    * [ ] Set **Global database identifier** to `auroralab-mysql-global`

2. In the **AWS Region** section:
    * [ ] Choose the **Secondary region** of `Us East (N. Virginia)`

3. In the **Connectivity** section, expand the sub-section called **Additional connectivity configuration**. This section allows you to specify where the database cluster will be deployed within your defined network configuration created above:
    * [ ] Set **Virtual Private Cloud (VPC)** to `auroralab-vpc`
    * [ ] Ensure the selected **Subnet Group** matches the stack name (e.g. `auroralab-dbsubnets-[hash]`)
    * [ ] Make sure the **Publicly accessible** option is set to `No`
    * [ ] For **VPC security group** select **Choose existing** and pick the security group named `auroralab-database-sg`, remove any other security groups, such as `default` from the selection

4. Expand the **Advanced configuration** section, and configure the following options:
    * [ ] Set **DB instance identifier** to `auroralab-mysql-node-3`
    * [ ] Set **DB cluster identifier** to `auroralab-mysql-secondary`
    * [ ] For **DB cluster parameter group** select the group with the stack name in the name (e.g. `auroralab-[...]`)
    * [ ] For **DB parameter group** select the group with the stack name in the name (e.g. `auroralab-[...]`)
    * [ ] Set **Backup retention period** to `1 day`
    * [ ] **Check** the box for **Enable Performance Insights**
    * [ ] Set **Retention period** to `Default (7 days)`
    * [ ] Set **Master key** to `[default] aws/rds`
    * [ ] **Check** the box for **Enable Enhanced Monitoring**
    * [ ] Set **Granularity** to `1 second`
    * [ ] Set **Monitoring Role** to `auroralab-monitor-us-east-1`

!!! note
    Please note there are **two** monitoring roles in the list, one for the primary region (the one in the top right corner of your web page), the other for the secondary region (typically `us-east-1`). At this step, you need the **secondary** region one.

<span class="image">![RDS Cluster Add Region](rds-cluster-add-region.png?raw=true)</span>

??? tip "What do these selections mean?"
    You will create a global cluster, a secondary DB cluster, and DB instance in that secondary cluster, with associated configurations in one step. Your existing DB cluster will become the primary DB cluster in the new global cluster. These are distinct API calls to the RDS service should you create a global cluster using the AWS CLI, SDKs or other tools. The RDS service console, simply combines these distinct steps into a single operation.

Click **Add region** to provision the global cluster.

!!! note
    Creating a global cluster based on the existing DB cluster is a seamless operation, your workload will not experience any disruption. You can monitor the performance metrics of the load generator started above, throughout this operation to validate.

The global cluster, including the secondary DB cluster and instance may take up to 30 minutes to provision.

In order to connect to the DB cluster and start using it, you need to retrieve the DB cluster endpoints. Unlike a regular DB cluster, only the **Reader Endpoint** is provisioned. The **Cluster Endpoint** is not being provisioned, as secondary DB clusters only contain readers, and cannot accept writes. The **Reader Endpoint** will always resolve to one of the reader DB instances and should be used for low latency read operations within that region. In the RDS console, go to the DB cluster detail view by clicking on the cluster DB identifier for the secondary DB cluster, named `auroralab-mysql-secondary`.

The **Endpoints** section in the **Connectivity and security** tab of the details page displays the endpoints. Note these values down, as you will use them later.

<span class="image">![RDS Cluster Secondary Endpoints](rds-cluster-secondary-endpoints.png?raw=true)</span>


