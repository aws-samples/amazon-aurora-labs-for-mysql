# Creating a New Aurora Cluster

!!! note
    If you are familiar with the basic concepts of Amazon Aurora MySQL, and have created a cluster in the past, you may skip this module, by using provisioning the lab environment using the [**lab-with-cluster.yml**](https://[[website]]/templates/lab-with-cluster.yml) CloudFormation template, so the DB cluster is provisioned for you. Skip to [Connecting, Loading Data and Auto Scaling](/modules/connect/).

This lab will walk you through the steps of creating an Amazon Aurora database cluster manually, and configuring app the parameters required for the cluster components. At the end of this lab you will have a database cluster ready to be used in subsequent labs.

This lab contains the following tasks:

1. Creating the DB cluster
2. Retrieving the DB cluster endpoints
3. Assigning an IAM role to the DB cluster
4. Creating a replica auto scaling policy

## 1. Creating the DB cluster

Open the <a href="https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2" target="_blank">Amazon RDS service console</a>.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Click **Create database** to start the configuration process

!!! note
    The RDS console database creation workflow has been simplified recently. Depending on your previous usage of the RDS console UI, you may see the old workflow or the new one, you may also be presented with a prompt to toggle between them. In this lab we are using the new workflow for reference, although the steps will work similarly in the old console workflow as well, if you are more familiar with it.

<span class="image">![Create Database](1-create-database.png?raw=true)</span>

In the first configuration section of the **Create database** page, called **Database settings** ensure the **Easy create** toggle button is turned **OFF** (grey color).

Next, in the **Engine options** section, choose the **Amazon Aurora** engine type, the **Amazon Aurora with MySQL compatibility edition, the **Aurora (MySQL)-5.6.10a** version and the **Regional** database location.

<span class="image">![Engine Options](1-engine-options.png?raw=true)</span>

In the **Database features** section, select **One writer and multiple readers**, and in the **Templates** section, select **Production**. The selections so far will instruct AWS to create an Aurora MySQL database cluster with the most recent version of the MySQL 5.6 compatible engine in a highly available configuration with one writer and one reader database instance in the cluster.

In the **Settings** section give your database cluster a recognizable identifier, such as `labstack-cluster`. Configure the name and password of the master database user, with the most elevated permissions in the database. We recommend to use the user name `masteruser` for consistency with subsequent labs and a password of your choosing. For simplicity ensure the check box **Auto generate a password** is **not checked**.

<span class="image">![Database Settings](1-db-settings.png?raw=true)</span>

In the **Connectivity** section, expand the sub-section called **Additional connectivity configuration**. This section allows you to specify where the database cluster will be deployed within your defined network configuration. To simplify the labs, the CloudFormation stack you deployed in the preceding [Prerequisites](/modules/prerequisites/) module, has configured a VPC that includes all resources needed for an Aurora database cluster. This includes the VPC itself, subnets, DB subnet groups, security groups and several other networking constructs. All you need to do is select the appropriate existing connectivity controls in this section.

Pick the **Virtual Private Cloud (VPC)** named after the CloudFormation stack name, such as `labstack-vpc`. Similarly make sure the selected **Subnet Group** also matches the stack name (e.g. `labstack-dbsubnets-[hash]`). Make sure the cluster **Publicly accessible** option is set to **No**. The lab environment also configured a **VPC security group** that allows your lab workspace EC2 instance to connect to the database. Make sure the **Choose existing** security group option is selected and from the dropdown pick the security group with a name ending in `-mysql-internal` (eg. `labstack-mysql-internal`). Please remove any other security groups, such as `default` from the selection.

<span class="image">![Connectivity](1-connectivity.png?raw=true)</span>

Next, expand the **Advanced configuration** section. Set the **Initial database name** to `mylab`. For the **DB cluster parameter group** and **DB parameter group** selectors, choose the groups with the stack name in their name (e.g. `labstack-[...]`). Choose a `7 days` **Backup retention period**. Check the box to **Enable encryption** and select the `[default] aws/rds` for the **Master key**.

<span class="image">![Advanced configuration](1-advanced-1.png?raw=true)</span>

Enable the backtrack capability by checking the **Enable Backtrack** box and set a **Target backtrack window** of `24` hours. Check the box to **Enable Performance Insights** with a **Retention period of `Default (7 days)` and use the `[default] aws/rds` **Master key** for monitoring data encryption. Next, check the **Enable Enhanced Monitoring** box, and select a **Granularity** of `1 second`. For **Log exports** check the **Error log** and **Slow query log** boxes.

<span class="image">![Advanced configuration](1-advanced-2.png?raw=true)</span>

Also in the **Advanced configuration** section, de-select the check box **Enable delete protection**. In a production use case, you will want to leave that option checked, but for testing purposes, un-checking this option will make it easier to clean up the resources once you have completed the labs.

Before continuing, let's summarize the configuration options selected. You will create a database cluster with the following characteristics:

* Aurora MySQL 5.6 compatible (latest stable engine version)
* Regional cluster composed of a writer and a reader DB instance in different availability zones (highly available)
* Deployed in the VPC and using the network configuration of the lab environment
* Using custom database engine parameters that enable the slow query log, S3 access and tune a few other configurations
* Automatically backed up continuously, retaining backups for 7 days
* Using data at rest encryption
* Retaining 24 hours worth of change data for backtrack purposes
* With Enhanced Monitoring and Performance Insights enabled

Click **Create database** to provision the DB cluster.

<span class="image">![Advanced configuration - end](1-advanced-3.png?raw=true)</span>

## 2. Retrieving the DB cluster endpoints

The database cluster may take several minutes to provision, including the DB instances making up the cluster. In order to connect to the DB cluster and start using it in subsequent labs, you need to retrieve the DB cluster endpoints. There are two endpoints created by default. The **Cluster Endpoint** will always point to the **writer** DB instance of the cluster, and should be used for both writes and reads. The **Reader Endpoint** will always resolve to one of the **
reader** DB instances and should be used to offload read operations to read replicas. In the RDS console, go to the DB cluster detail view by clicking on the cluster DB identifier.

<span class="image">![DB Cluster Status](2-db-cluster-status.png?raw=true)</span>

The **Endpoints** section in the **Connectivity and security** tab of the details page displays the endpoints. Note these values down, as you will use them later.

<span class="image">![DB Cluster Endpoints](2-db-cluster-details.png?raw=true)</span>

## 3. Assigning an IAM role to the DB cluster

Once created, you should assign an IAM role to the DB cluster, in order to allow the cluster access to Amazon S3 for importing and exporting data. The IAM role has already been created using CloudFormation when you created the lab environment. On the same DB cluster detail page as before, in the **Manage IAM roles** section, choose the IAM role named after the stack name, ending in `-integrate-[region]` (e.g. `labstack-integrate-[region]`). Then click **Add role**.

<span class="image">![DB Cluster Add Role](3-add-role.png?raw=true)</span>

Once the operation completes the **Status** of the role will change from `Pending` to `Active`.

## 4. Creating a replica auto scaling policy

Finally, you will add a read replica auto scaling configuration to the DB cluster. This will allow the DB cluster to scale the number of reader DB instances that operate in the DB cluster at any given point in time based on the load.

In the top right corner of the details page, click on **Actions** and then on **Add replica auto scaling**.

<span class="image">![DB Cluster Add Auto Scaling](4-add-as-policy.png?raw=true)</span>

Provide a **Policy name** based on the stack name, such as `labstack-autoscale-readers`. For the **Target metric** choose **Average CPU utilization of Aurora Replicas**. Enter a **Target value** of `20` percent. In a production use case this value may need to be set much higher, but we are using a lower value for demonstration purposes. Next, expand the **Additional configuration** section, and change both the **Scale in cooldown period** and **Scale out cooldown period** to a value of `180` seconds. This will reduce the time you have to wait between scaling operations in subsequent labs.

In the **Cluster capacity details** section, set the **Minimum capacity** to `1` and **Maximum capacity** to `2`. In a production use case you may need to use different values, but for demonstration purposes, and to limit the cost of associated with the labs we limit the number of readers to two. Next click **Add policy**.

<span class="image">![Auto Scaling Configuration](4-as-policy-config.png?raw=true)</span>
