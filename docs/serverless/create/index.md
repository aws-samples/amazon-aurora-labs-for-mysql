# Create an Aurora Serverless DB Cluster

This lab will walk you through the steps of creating an Amazon Aurora Serverless database cluster manually, and configuring the scaling parameters of the cluster.

This lab contains the following tasks:

1. Create a serverless DB cluster
2. Create a secret to store the credentials

This lab requires the following lab modules to be completed first:

* [Deploy Environment](/prereqs/environment/) (using the `lab-no-cluster.yml` template is sufficient)


## 1. Create a serverless DB cluster

Open the <a href="https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2" target="_blank">Amazon RDS service console</a>.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Click **Create database** to start the configuration process

<span class="image">![Create Database](1-create-database.png?raw=true)</span>

In the first configuration section of the **Create database** page, ensure the **Standard Create** database creation method is selected.

Next, in the **Engine options** section, choose the **Amazon Aurora** engine type, the **Amazon Aurora with MySQL compatibility edition, the **Aurora (MySQL)-5.6.10a** version and the **Regional** database location.

<span class="image">![Engine Options](1-engine-options.png?raw=true)</span>

In the **Database features** section, select **Serverless**. The selections so far will instruct AWS to create an Aurora MySQL database cluster with the most recent version of the MySQL 5.6 compatible engine in a serverless configuration.

In the **Settings** section set the database cluster identifier to `labstack-serverless`. Configure the name and password of the master database user, with the most elevated permissions in the database. We recommend to use the user name `masteruser` for consistency with subsequent labs and a password of your choosing. For simplicity ensure the check box **Auto generate a password** is **not checked**.

<span class="image">![Database Settings](1-serverless-settings.png?raw=true)</span>

In the **Capacity settings** section, choose a **Minimum Aurora capacity unit** of `1 (2GB RAM)` and a **Maximum Aurora capacity unit** of `16 (32 GB RAM)`. Next, expand the **Additional scaling configuration** section, and **check** the box next to **Pause compute capacity after consecutive minutes of inactivity**. This configuration will allow Aurora Serverless to scale the capacity of your DB cluster between 1 capacity unit and 32 capacity units, and to suspect capacity entirely after 5 minutes of inactivity.

In the **Connectivity** section, expand the sub-section called **Additional connectivity configuration**. This section allows you to specify where the database cluster will be deployed within your defined network configuration. To simplify the labs, the CloudFormation stack you deployed in the preceding [Prerequisites](/modules/prerequisites/) module, has configured a VPC that includes all resources needed for an Aurora database cluster. This includes the VPC itself, subnets, DB subnet groups, security groups and several other networking constructs. All you need to do is select the appropriate existing connectivity controls in this section.

Pick the **Virtual Private Cloud (VPC)** named after the CloudFormation stack name, such as `labstack-vpc`. Similarly make sure the selected **Subnet Group** also matches the stack name (e.g. `labstack-dbsubnets-[hash]`). The lab environment also configured a **VPC security group** that allows your lab workspace EC2 instance to connect to the database. Make sure the **Choose existing** security group option is selected and from the dropdown pick the security group with a name ending in `-mysql-internal` (eg. `labstack-mysql-internal`). Please remove any other security groups, such as `default` from the selection.

Additionally, please check the box **Data API**, to enable integration with the RDS Data API.

<span class="image">![Capacity and Connectivity](1-serverless-capacity.png?raw=true)</span>

Next, expand the **Advanced configuration** section. Choose a `1 day` **Backup retention period**. **De-select** the check box **Enable delete protection**. In a production use case, you will want to leave that option checked, but for testing purposes, un-checking this option will make it easier to clean up the resources once you have completed the labs.

<span class="image">![Advanced configuration](1-serverless-advconfig.png?raw=true)</span>

??? tip "What do these selections mean?"
    You will create a database cluster with the following characteristics:

    * Aurora MySQL 5.6 compatible (latest engine version)
    * Serverless db cluster scaling between 1 and 16 capacity units, and pausing compute capacity after 5 minutes of inactivity
    * Deployed in the VPC and using the network configuration of the lab environment
    * Integrated with the RDS Data API
    * Automatically backed up continuously, retaining backups for 7 days
    * Using data at rest encryption

Click **Create database** to provision the DB cluster.

Once back to the list of databases, click the name of the new database in the listing.

<span class="image">![Select Cluster](1-serverless-selection.png?raw=true)</span>

In the details view of the cluster, click on the **Configuration** tab. Note the value for **ARN**. Write this down, you will need it later.

<span class="image">![CLuster ARN](1-serverless-arn.png?raw=true)</span>


## 2. Create a secret to store the credentials

Open the <a href="https://us-west-2.console.aws.amazon.com/secretsmanager/home?region=us-west-2" target="_blank">AWS Secrets Manager service console</a>.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Click **Store a new secret** to start the configuration process.

<span class="image">![Create Secret](2-create-secret.png?raw=true)</span>

In the **Select secret type** section, choose **Credentials for RDS database**, then input the **User name** (e.g. `masteruser`) and **Password** that you provided when you created the serverless DB cluster.

Next, in the **Select which RDS database this secret will access** section, choose the DB cluster identifier you assigned to your cluster (e.g. `labstack-serverless`). Click **Next**.

<span class="image">![Configure Secret](2-config-secret.png?raw=true)</span>

Name the secret `labstack-serverless-secret` and provide a relevant description for the secret, then click **Next**.

<span class="image">![Name Secret](2-name-secret.png?raw=true)</span>

Finally, in the **Configure automatic rotation** section, leave the option of **Disable automatic rotation** selected. In a production environment you will want to use database credentials that rotate automatically for additional security. Click **Next**.

<span class="image">![Rotate Secret](2-rotate-secret.png?raw=true)</span>

In the **Review** section you have the ability to check the configuration parameters for your secret, before it gets created. Additionally, you can retrieve sample code in popular programming languages, so you can easily retrieve secrets into your application. Click **Store** at the bottom of the screen.

Once created, identify the **ARN** of the newly created secret. This value will be needed in subsequent labs. In the list of **Secrets** in the console, click on the name of the newly created secret.

<span class="image">![List Secrets](2-list-secrets.png?raw=true)</span>

In the detail view of the secret, note the value for **Secret ARN**. Write this down, you will need it later.

<span class="image">![Secret ARN](2-arn-secret.png?raw=true)</span>
