# Win the Data! Hands-on with Amazon Aurora

In this session, learn how to leverage the unique features of the Amazon Aurora platform to build faster, more scalable database applications optimized for the cloud.

Let's get started!

## Sign in to the provided AWS account

At the beginning of the workshop you have been provided with a **12-character access code**. This access code grants you permission to use a dedicated AWS account for the purposes of this workshop.

Go to <a href="https://dashboard.eventengine.run/" target="_blank">**https://dashboard.eventengine.run/**</a>, enter the access code and click **Proceed**.

<span class="image">![EventEngine Login](ee-login.png?raw=true)</span>

On the **Team Dashboard**, please click **AWS Console** to log into the AWS Management Console.

<span class="image">![EventEngine Dashboard](ee-dashboard.png?raw=true)</span>

Click **Open Console**. For the purposes of this workshop, you will not need to use command line and API access credentials.

<span class="image">![EventEngine Open Console](ee-open-console.png?raw=true)</span>

## Overview of labs

For your convenience, a lab environment has already been deployed for you. The lab environment contains the following resources:

1. **Two Amazon Aurora database clusters**, one running PostgreSQL, the other running MySQL. They are named **labstack-postgres-cluster** and **labstack-mysql-cluster**. Each DB cluster contains two database instances (with names ending in node-1 and node-2), deployed each in two separate Availability Zones for Multi-AZ high availability. One of the DB instances is a writer (master), the other a reader (read-only replica).
2. **Two EC2-based workstations**, one containing the necessary software to complete the Aurora PostgreSQL labs, the other to be used for the Aurora MySQL labs. You will connect to them using <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html" target="_blank">AWS Systems Manager</a> - Session Manager, following the instructions provided. You do not need to install any client software on your computer.
3. Supporting resources and network configuration, including: <a href="https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html" target="_blank">VPC</a>, subnets, gateways, subnet groups, security groups, IAM roles, credentials stored in an <a href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html" target="_blank">AWS Secrets Manager</a> secret.


<!--


Time permitting, you will run the following hands-on labs. Start with the [prerequisites](/reinvent/prerequisites/).

# | Lab Module | Recommendation | Overview
--- | --- | --- | ---
1 | [**Prerequisites**](/reinvent/prerequisites/) | **Required, start here** | Set up the lab environment and provision the prerequisite resources
2 | [**Connecting, Loading Data and Auto Scaling**](/reinvent/connect/) | Recommended, for provisioned clusters | Connect to the DB cluster for the first time, load an initial data set and test read replica auto scaling. The initial data set may be used in subsequent labs.
3 | [**Cloning Clusters**](/reinvent/clone/) | Recommended, for provisioned clusters | Clone an Aurora DB cluster and observing the divergence of the data set.
4 | [**Backtracking a Cluster**](/reinvent/backtrack/) | Recommended, for provisioned clusters | Backtrack an Aurora DB cluster to fix an accidental DDL operation.
5 | [**Using Performance Insights**](/reinvent/perf-insights/) | Recommended, for provisioned clusters | Examine the performance of your DB instances using RDS Performance Insights
6 | [**Creating a Serverless Aurora Cluster**](/reinvent/create-serverless/) | Recommended, for serverless clusters | Create a new Amazon Aurora Serverless MySQL DB cluster manually. You may skip the provisioned cluster labs if you are planning to operate a serverless workload.
7 | [**Using Aurora Serverless with Lambda Functions**](/reinvent/connect-serverless/) | Recommended, for serverless clusters | Connect to your serverless cluster using the RDS Data API and Lambda functions. Requires the previous lab.

## Lab environment at a glance

To ensure everyone has a consistent experience, we have created a foundational template for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provisions the resources needed for the lab environment.

<div class="architecture"><img src="/assets/images/generic-architecture.png"></div>

The environment deployed using CloudFormation includes several components:

*	a <a href="https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html" target="_blank">Amazon VPC</a> network configuration with public and private subnets
*	a <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html#USER_VPC.Subnets" target="_blank">Database subnet group</a> and relevant <a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html" target="_blank">security groups</a> for the cluster and workstation
*	a <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Instances.html" target="_blank">Amazon EC2 instance</a> configured with the software components needed for the lab
*	<a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html" target="_blank">IAM roles</a> with access permissions for the workstation and cluster permissions for <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html" target="_blank">enhanced monitoring</a>, S3 access and logging
*	Custom cluster and DB instance <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithParamGroups.html" target="_blank">parameter groups</a> for the Amazon Aurora cluster, enabling logging and performance schema
*	an <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html" target="_blank">Amazon Aurora</a> MySQL DB cluster with 2 nodes: a writer and read replica
* the master database credentials will be generated automatically and stored in an <A href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html" target="_blank">AWS Secrets Manager</a> secret.
*	a <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Integrating.AutoScaling.html" target="_blank">read replica auto scaling</a> configuration
*	a <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html" target="_blank">AWS Systems Manager</a> command document to execute a load test
-->
