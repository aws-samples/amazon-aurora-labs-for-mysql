# Getting Started

## Create an AWS account
In order to complete the hands-on content on this site, you'll need an AWS Account. We strongly recommend that you use a personal account or create a new AWS account to ensure you have the necessary access and that you do not accidentally modify corporate resources. Do not use an AWS account from the company you work for unless they provide sandbox accounts just for this purpose.

If you are setting up an AWS account for the first time, follow the instructions below to [create an administrative IAM user account](#create-an-iam-user-with-admin-permissions), we recommend not using your AWS account root credentials for day to day usage. If you have received credits to complete these labs follow the instructions below on [adding the credits](#add-credits-optional) to your AWS account.

## Overview of labs

The following labs are currently available, part of this instructional website.

???+ abstract "Prerequisites"
    You will need to complete the following prerequisite labs before running any other labs. **Do this first!**

    # | Lab Module | Recommendation | Overview
    --- | --- | --- | ---
    1 | [**Deploy Environment**](/prereqs/environment/) | **Required, start here** | Set up the lab environment and provision the prerequisite resources.
    2 | [**Connect to the Session Manager Workstation**](/prereqs/connect/) | **Required** | Connect to the EC2 based workstation using Session Manager, so you can interact with the database.


??? abstract "Labs for Aurora Provisioned DB clusters"
    # | Lab Module | Recommendation | Overview
    --- | --- | --- | ---
    1 | [**Create a New DB Cluster**](/provisioned/create/) | Optional | Create a new Amazon Aurora MySQL DB cluster manually. This is optional, as you can also deploy the environment with a cluster provisioned automatically for you.
    2 | [**Connect, Load Data and Auto Scale**](/provisioned/interact/) | Recommended | Connect to the DB cluster, load an initial data set from S3 and test read replica auto scaling. The initial data set may be used in subsequent labs.
    3 | [**Clone a DB Cluster**](/provisioned/clone/) | Recommended | Clone an Aurora DB cluster and observing the divergence of the data set.
    4 | [**Backtrack a DB Cluster**](/provisioned/backtrack/) | Recommended | Backtrack an Aurora DB cluster to fix an accidental DDL operation.
    5 | [**Use Performance Insights**](/provisioned/perf-insights/) | Recommended | Examine the performance of your DB instances using RDS Performance Insights.
    6 | [**Test Fault Tolerance**](/provisioned/failover/) | Recommended | Examine the failover process in Amazon Aurora MySQL and how it can be optimized.

??? abstract "Labs for Aurora Serverless DB clusters"
    # | Lab Module | Recommendation | Overview
    --- | --- | --- | ---
    1 | [**Create an Aurora Serverless DB cluster**](/serverless/create/) | Required | Create a new Amazon Aurora Serverless MySQL DB cluster manually.
    2 | [**Use Aurora Serverless with AWS Lambda functions**](/serverless/dataapi/) | Recommended | Connect to your DB cluster using the RDS Data API and Lambda functions.

You can also discover exercises, labs and workshops related to Amazon Aurora on the [Related Labs and Workshops](/related/labs/) page.

## Lab environment at a glance

To simplify the getting started experience with the labs, we have created foundational templates for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provision the resources needed for the lab environment. These templates are designed to deploy a consistent networking infrastructure, and client-side experience of software packages and components used in the lab.

<div class="architecture"><img src="/assets/images/generic-architecture.png"></div>

The environment deployed using CloudFormation includes several components:

*	<a href="https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html" target="_blank">Amazon VPC</a> network configuration with public and private subnets
*	<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html#USER_VPC.Subnets" target="_blank">Database subnet group</a> and relevant <a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html" target="_blank">security groups</a> for the cluster and workstation
*	<a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Instances.html" target="_blank">Amazon EC2 instance</a> configured with the software components needed for the lab
*	<a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html" target="_blank">IAM roles</a> with access permissions for the workstation and cluster permissions for <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html" target="_blank">enhanced monitoring</a>, S3 access and logging
*	Custom cluster and DB instance <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithParamGroups.html" target="_blank">parameter groups</a> for the Amazon Aurora cluster, enabling logging and performance schema
*	Optionally, <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html" target="_blank">Amazon Aurora</a> DB cluster with 2 nodes: a writer and read replica
* If the cluster is created for you, the master database credentials will be generated automatically and stored in an <A href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html" target="_blank">AWS Secrets Manager</a> secret.
*	Optionally, <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Integrating.AutoScaling.html" target="_blank">read replica auto scaling</a> configuration
*	Optionally, <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html" target="_blank">AWS Systems Manager</a> command document to execute a load test

## Create an IAM user (with admin permissions)
If you don't already have an AWS IAM user with admin permissions, please use the following instructions to create one:

1. Browse to the <a href="https://console.aws.amazon.com/iam/" target="_blank">AWS IAM</a> console.
2. Click **Users** on the left navigation and then click **Add User**.
3. Enter a **User Name**, check the checkbox for **AWS Management Console access**, enter a **Custom Password**, and click **Next:Permissions**.
4. Click **Attach existing policies directly**, click the checkbox next to the **AdministratorAccess** policy, and click **Next:Review**.
5. Click **Create User**
6. Click **Dashboard** on the left navigation and use the **IAM users sign-in link** to login as the admin user you just created.


## Add credits (optional)
If you are doing these workshop as part of an AWS sponsored event that doesn't provide AWS accounts, you will receive credits to cover the costs. Below are the instructions for entering the credits:

1. Browse to the AWS Account Settings console.
2. Enter the Promo Code you received (these will be handed out at the beginning of the workshop).
3. Enter the Security Check and click Redeem.

## Additional software needed for labs

The templates and scripts setting up the lab environment install the following software in the lab environment for the purposes of deploying and running the labs:

* [mysql-client](https://dev.mysql.com/doc/refman/5.6/en/programs-client.html) package. MySQL open source software is provided under the GPL License.
* [sysbench](https://github.com/akopytov/sysbench) available using the GPL License.
* [test_db](https://github.com/datacharmer/test_db) available using the Creative Commons Attribution-Share Alike 3.0 Unported License.
* [Percona's sysbench-tpcc](https://github.com/Percona-Lab/sysbench-tpcc) available using the Apache License 2.0.
