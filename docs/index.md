# Amazon Aurora Labs for MySQL

<div class="aurora"><img src="/assets/images/amazon-aurora.svg"></div>

Welcome to the AWS workshop and lab content portal for <a href="https://aws.amazon.com/rds/aurora/details/mysql-details/" target="_blank">Amazon Aurora MySQL</a> compatible databases! Here you will find a collection of workshops and other hands-on content aimed at helping you gain an understanding of the Amazon Aurora features and capabilities.

The resources on this site include a collection of easy to follow instructions with examples, templates to help you get started and scripts automating tasks supporting the hands-on labs. These resources are focused on helping you discover how advanced features of the Amazon Aurora MySQL database operate. Prior expertise with AWS and MySQL-based databases is beneficial, but not required to complete the labs.


## Overview of labs

The following labs are currently available, click on the relevant tab to see the labs for that topic:

=== "Prerequisites"
    You will need to complete the following prerequisites before running any other labs. **Do this first!**

    # | Lab Module | Recommendation | Overview
    --- | --- | --- | ---
    P1 | [**Get started using the lab environment**](/prereqs/environment/) | **Required, start here** | Set up the lab environment and provision the prerequisite resources.
    P2 | [**Connect to the Session Manager workstation**](/prereqs/connect/) | **Required** | Connect to the EC2 based workstation using Session Manager, so you can interact with the database.


=== "Provisioned"
    # | Lab Module | Recommendation | Overview
    --- | --- | --- | ---
    R1 | [**Create a New DB Cluster**](/provisioned/create/) | Optional | Create a new Amazon Aurora MySQL DB cluster manually. This is optional, as you can also deploy the environment with a cluster provisioned automatically for you.
    R2 | [**Connect, Load Data and Auto Scale**](/provisioned/interact/) | Recommended | Connect to the DB cluster, load an initial data set from S3 and test read replica auto scaling. The initial data set may be used in subsequent labs.
    R3 | [**Clone a DB Cluster**](/provisioned/clone/) | Recommended | Clone an Aurora DB cluster and observing the divergence of the data set.
    R4 | [**Backtrack a DB Cluster**](/provisioned/backtrack/) | Recommended | Backtrack an Aurora DB cluster to fix an accidental DDL operation.
    R5 | [**Use Performance Insights**](/provisioned/perf-insights/) | Recommended | Examine the performance of your DB instances using RDS Performance Insights.
    R6 | [**Test Fault Tolerance**](/provisioned/failover/) | Recommended | Examine the failover process in Amazon Aurora MySQL and how it can be optimized.
    R7 | [**Set up Database Activity Streams**](/provisioned/das/) | Recommended | Monitor your database activity by using Database Activity Streams.


=== "Serverless"
    # | Lab Module | Recommendation | Overview
    --- | --- | --- | ---
    S1 | [**Create an Aurora Serverless DB cluster**](/serverless/create/) | Required | Create a new Amazon Aurora Serverless MySQL DB cluster manually.
    S2 | [**Use Aurora Serverless with AWS Lambda functions**](/serverless/dataapi/) | Recommended | Connect to your DB cluster using the RDS Data API and Lambda functions.


=== "Global Database"
    # | Lab Module | Recommendation | Overview
    --- | --- | --- | ---
    G1 | [**Deploy a Global Database**](/global/deploy/) | Required | Create a Global Database which will span across multiple regions.
    G3 | [**Connect an Application**](/global/biapp/) | Recommended | Connect a Business Intelligence application to the Global Database.
    G4 | [**Monitor a Global Database**](/global/monitor/) | Recommended | Create an Amazon CloudWatch Dashboard to monitor the latency, replicated I/O, and the cross region replication data transfer of the Global Database.
    G4 | [**Use Write Forwarding**](/global/wfwd/) | Recommended | Use a simple application to understand and experience the different consistency modes available with the Global Database Write Forwarding feature.
    G5 | [**Fail Over a Global Database**](/global/failover/) | Recommended | Simulate a regional failure and DR scenario, and promote the secondary region in a Global Database.
    G6 | [**Fail Back a Global Database**](/global/failback/) | Optional | Restore full operations in the original primary region for the Global Database after a failover.


=== "Machine Learning"
    # | Lab Module | Recommendation | Overview
    --- | --- | --- | ---
    M1 | [**Overview and Prerequisites**](/ml/overview/) | Required | Setup a sample schema and data for machine learning integration.
    M2 | [**Use Comprehend with Aurora**](/ml/comprehend/) | Recommended | Integrate Aurora with the Comprehend Sentiment Analysis API and make sentiment analysis inferences via SQL commands.
    M3 | [**Use SageMaker with Aurora**](/ml/sagemaker/) | Recommended | Integrate Aurora with SageMaker Endpoints to infer customer churn in a data set using SQL commands.
    M4 | [**Cleanup Lab Resources**](/ml/cleanup/) | Recommended | Clean up after the labs and remove unneeded AWS resources.       

You can also discover other exercises, labs and workshops related to Amazon Aurora on the [Related Labs and Workshops](/related/labs/) page.


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


## Additional software needed for labs

You do not need any special software on the computer you are using for these labs, except an up to date web browser. The templates and scripts setting up the lab environment install the following software in the lab environment for the purposes of deploying and running the labs:

* [mysql-client](https://dev.mysql.com/doc/refman/5.6/en/programs-client.html) package. MySQL open source software is provided under the GPL License.
* [sysbench](https://github.com/akopytov/sysbench) available using the GPL License.
* [test_db](https://github.com/datacharmer/test_db) available using the Creative Commons Attribution-Share Alike 3.0 Unported License.
* [Percona's sysbench-tpcc](https://github.com/Percona-Lab/sysbench-tpcc) available using the Apache License 2.0.
* [Apache Superset](https://superset.apache.org/index.html) available using the Apache License 2.0.
