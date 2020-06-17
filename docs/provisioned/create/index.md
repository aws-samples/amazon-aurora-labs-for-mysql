# Create a New Aurora Cluster

This lab will walk you through the steps of creating an Amazon Aurora database cluster manually, and configuring app the parameters required for the cluster components. At the end of this lab you will have a database cluster ready to be used in subsequent labs.

!!! tip "Do you already know how to create a DB cluster?"
    If you are familiar with the basic concepts of Amazon Aurora MySQL, and have created a cluster in the past, you may skip this module by provisioning the lab environment using the option to have the DB cluster deployed automatically. See the [Get Started](prereqs/environment/) prerequisites module for details on provisioning the lab environment. Skip to [Connect, Load Data and Auto Scale](/provisioned/interact/).

    If you are running these labs in a formal, organized workshop event, please follow the recommendations of your instructors, and ask any lab assistant for help if you have questions about this lab.

This lab contains the following tasks:

1. Create the DB cluster
2. Retrieve the DB cluster endpoints
3. Assign an IAM role to the DB cluster
4. Create a replica auto scaling policy
5. Create an AWS Secrets Manager secret
6. Configure the client workstation
7. Verify DB cluster

This lab requires the following lab modules to be completed first:

* [Get Started](/prereqs/environment/) (you do not need to provision a DB cluster automatically)
* [Connect to the Session Manager Workstation](/prereqs/connect/) (needed for task \#6)

## 1. Create the DB cluster

Open the <a href="https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2" target="_blank">Amazon RDS service console</a>.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Click **Create database** to start the configuration process

<span class="image">![Create Database](1-create-database.png?raw=true)</span>

In the **Choose a database creation method** section, ensure the **Standard Create** option is selected.

Next, in the **Engine options** section, choose the **Amazon Aurora** engine type, the **Amazon Aurora with MySQL compatibility** edition, the **Aurora (MySQL 5.7) 2.07.2** version and the **Regional** database location.

<span class="image">![Engine Options](1-engine-options.png?raw=true)</span>

In the **Database features** section, select **One writer and multiple readers**, and in the **Templates** section, select **Production**.

??? tip "What do these selections mean?"
    The selections so far will instruct AWS to create an Aurora MySQL database cluster with the specified version of the MySQL 5.7 compatible engine in a highly available configuration with one writer and one reader database instance in the cluster. This is called an **Aurora provisioned DB cluster**, because you indicate the specific type of compute capacity that powers your cluster. If you wish to create an Aurora Serverless DB cluster, and test the Aurora Serverless functionality, we have [a different lab for you](/serverless/create/).

In the **Settings** section, set the **DB cluster identifier** to `auroralab-mysql-cluster`. Configure the name and password of the master database user, with the most elevated permissions in the database. We recommend to use the user name `masteruser` for consistency with subsequent labs and a password of your choosing. For simplicity ensure the check box **Auto generate a password** is **not checked**.

<span class="image">![Database Settings](1-db-settings.png?raw=true)</span>

In the **DB instance size** section, select **Memory Optimized classes**, and choose `r5.large` in the size drop-down. In the **Availability & durability** section, choose **Create an Aurora Replica/Reader node in a different AZ**.

<span class="image">![Database Settings](1-db-size.png?raw=true)</span>


In the **Connectivity** section, expand the sub-section called **Additional connectivity configuration**. This section allows you to specify where the database cluster will be deployed within your defined network configuration. To simplify the labs, we have configured all the networking resources for you.

Pick the **Virtual Private Cloud (VPC)** named `auroralab-vpc`. The DB subnet group will be selected automatically once you choose the right VPC, please verify the selection is correct. The name of the DB subnet group should start either with `auroralab-dbsubnets-` or with `mod-` depending on the event you are participating in.

Make sure the cluster **Publicly accessible** option is set to **No**. The lab environment also configured a **VPC security group** that allows your lab workspace EC2 instance to connect to the database. Make sure the **Choose existing** security group option is selected and from the dropdown pick the security group named `auroralab-database-sg`. Please remove any other security groups, such as `default` from the selection.

In the **Database authentication** section, choose **Password and IAM database authentication** (IAM authentication may be used in some of the subsequent labs).

<span class="image">![Connectivity](1-connectivity.png?raw=true)</span>

Next, expand the **Advanced configuration** section. Set the **Initial database name** to `mylab`. For the **DB cluster parameter group** and **DB parameter group** selectors, choose the groups named starting with either `auroralab-[...]` or `mod-[...]`. Keep the `1 day` **Backup retention period**. Check the box to **Enable encryption** and select `[default] aws/rds` for the **Master key**.

<span class="image">![Advanced configuration](1-advanced-1.png?raw=true)</span>

Enable the backtrack capability by checking the **Enable Backtrack** box and set a **Target backtrack window** of `24` hours. Check the box to **Enable Performance Insights** with a **Retention period of `Default (7 days)` and use the `[default] aws/rds` **Master key** for monitoring data encryption. Next, check the **Enable Enhanced Monitoring** box, and select a **Granularity** of `1 second`.

<span class="image">![Advanced configuration](1-advanced-2.png?raw=true)</span>

Also in the **Advanced configuration** section, for **Log exports** check the **Error log** and **Slow query log** boxes. De-select the check box **Enable delete protection**. In a production use case, you will want to leave that option checked, but for testing purposes, un-checking this option will make it easier to clean up the resources once you have completed the labs.

??? tip "What do these selections mean?"
    You will create a database cluster with the following characteristics:

    * Aurora MySQL 5.7 compatible
    * Regional cluster composed of a writer and a reader DB instance in different availability zones (highly available)
    * Deployed in the VPC and using the network configuration of the lab environment
    * Using custom database engine parameters that enable the slow query log, S3 access and tune a few other configurations
    * Automatically backed up continuously, retaining backups for 7 days
    * Using data at rest encryption
    * Retaining 24 hours worth of change data for backtrack purposes
    * With Enhanced Monitoring and Performance Insights enabled

Click **Create database** to provision the DB cluster.

<span class="image">![Advanced configuration - end](1-advanced-3.png?raw=true)</span>


## 2. Retrieve the DB cluster endpoints

The database cluster may take several minutes to provision, including the DB instances making up the cluster. In order to connect to the DB cluster and start using it in subsequent labs, you need to retrieve the DB cluster endpoints. There are two endpoints created by default. The **Cluster Endpoint** will always point to the **writer** DB instance of the cluster, and should be used for both writes and reads. The **Reader Endpoint** will always resolve to one of the **reader** DB instances and should be used to offload read operations to read replicas. In the RDS console, go to the DB cluster detail view by clicking on the cluster DB identifier.

<span class="image">![DB Cluster Status](2-db-cluster-status.png?raw=true)</span>

The **Endpoints** section in the **Connectivity and security** tab of the details page displays the endpoints. Note these values down, as you will use them later.

<span class="image">![DB Cluster Endpoints](2-db-cluster-details.png?raw=true)</span>


## 3. Assign an IAM role to the DB cluster

Once created, you should assign an IAM role to the DB cluster, in order to allow the cluster access to Amazon S3 for importing and exporting data. The IAM role has already been created foryou with the lab environment. On the same DB cluster detail page as before, in the **Manage IAM roles** section, choose **Select IAM roles to add to this cluster** and pick the IAM role named starting with `auroralab-integrate-[region]` from the dropdown. If more than one role with that prefix is available, choose the one for the current region you are operating in. Then click **Add role**.

<span class="image">![DB Cluster Add Role](3-add-role.png?raw=true)</span>

Once the operation completes the **Status** of the role will change from `Pending` to `Active`.


## 4. Create a replica auto scaling policy

Finally, you will add a read replica auto scaling configuration to the DB cluster. This will allow the DB cluster to scale the number of reader DB instances that operate in the DB cluster at any given point in time based on the load.

In the top right corner of the details page, click on **Actions** and then on **Add replica auto scaling**.

<span class="image">![DB Cluster Add Auto Scaling](4-add-as-policy.png?raw=true)</span>

Set the **Policy name** based on the stack name: `auroralab-autoscale-readers`. For the **Target metric** choose **Average CPU utilization of Aurora Replicas**. Enter a **Target value** of `20` percent. In a production use case this value may need to be set much higher, but we are using a lower value for demonstration purposes. Next, expand the **Additional configuration** section, and change both the **Scale in cooldown period** and **Scale out cooldown period** to a value of `180` seconds. This will reduce the time you have to wait between scaling operations in subsequent labs.

In the **Cluster capacity details** section, set the **Minimum capacity** to `1` and **Maximum capacity** to `2`. In a production use case you may need to use different values, but for demonstration purposes, and to limit the cost associated with the labs we limit the number of readers to two. Next click **Add policy**.

<span class="image">![Auto Scaling Configuration](4-as-policy-config.png?raw=true)</span>


## 5. Create an AWS Secrets Manager secret

Open the <a href="https://us-west-2.console.aws.amazon.com/secretsmanager/home?region=us-west-2" target="_blank">AWS Secrets Manager service console</a>.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Click **Store a new secret** to start the configuration process.

<span class="image">![Create Secret](5-create-secret.png?raw=true)</span>

In the **Select secret type** section, choose **Credentials for RDS database**, then input the **User name** (should be `masteruser`) and **Password** that you provided when you created the DB cluster previously.

Next, in the **Select which RDS database this secret will access** section, choose the DB cluster identifier you assigned to your cluster (e.g. `auroralab-mysql-cluster`). Click **Next**.

<span class="image">![Configure Secret](5-config-secret.png?raw=true)</span>

Name the secret `secretCusterMasterUser` and provide a relevant description for the secret, then click **Next**.

<span class="image">![Name Secret](5-name-secret.png?raw=true)</span>

Finally, in the **Configure automatic rotation** section, leave the option of **Disable automatic rotation** selected. In a production environment you will want to use database credentials that rotate automatically for additional security. Click **Next**.

<span class="image">![Rotate Secret](5-rotate-secret.png?raw=true)</span>

In the **Review** section you have the ability to check the configuration parameters for your secret, before it gets created. Additionally, you can retrieve sample code in popular programming languages, so you can easily retrieve secrets into your application. Click **Store** at the bottom of the screen.

Once created, identify the **ARN** of the newly created secret. This value will be needed in subsequent labs. In the list of **Secrets** in the console, click on the name of the newly created secret.

<span class="image">![List Secrets](5-list-secrets.png?raw=true)</span>

In the detail view of the secret, note the value for **Secret ARN**. Write this down, you will need it later.

<span class="image">![Secret ARN](5-arn-secret.png?raw=true)</span>


## 6. Configure the EC2 workstation

Subsequent labs on this site use a consistent way to access DB credentials, regardless if the DB cluster was created manually or automatically. To simplify interactions, the lab credentials are saved in environment variables on the EC2 workstation you use to issue commands to the database. When the cluster is created automatically, the credentials are also set up for you. When you create the cluster manually, you need to run a few additional commands to reach parity.

If you are not already connected to the Session Manager workstation command line, please connect [following these instructions](/prereqs/connect/). Once connected, run the command below, replacing the ==[secretArn]== placeholder with the ARN of the secret created above:

```shell
CREDS=`aws secretsmanager get-secret-value --secret-id [secretArn] | jq -r '.SecretString'`
export DBUSER="`echo $CREDS | jq -r '.username'`"
export DBPASS="`echo $CREDS | jq -r '.password'`"
echo "export DBPASS=\"$DBPASS\"" >> /home/ubuntu/.bashrc
echo "export DBUSER=$DBUSER" >> /home/ubuntu/.bashrc
```

## 7. Verify DB cluster

Let's make sure your DB cluster has been created properly. First let's ensure the credentials have been saved correctly in the environment variables, run:

```shell
echo $DBUSER
```

You should see `masteruser` as the response string. Next, verify the version of the database engine created. Run the command below, replacing the ==[clusterEndpont]== placeholder with the value of the cluster endpoint created in the preceding steps:

```shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS" -e"SELECT @@aurora_version;"
```

You should see a response containing version number `2.07.2`.
