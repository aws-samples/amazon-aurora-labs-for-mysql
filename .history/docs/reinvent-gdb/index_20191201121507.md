# DAT348 - Amazon Aurora Global Database in Action

![AWS re:Invent 2019](/assets/images/reinvent19-topbanner.png)

In this hands-on workshop, learn how to achieve multi-region resilience for your application backend by using **Amazon Aurora Global Database**. We focus on patterns for multi-region database rollout and real-world use cases. Get hands-on and learn how Aurora global database allows you to scale your infrastructure without having to implement complicated multi-region patterns and see how to best leverage Aurora global database for fast cross-region disaster recovery and low-latency global reads.

## Requirements
* AWS Account (Temporary accounts will be provided for AWS Events)
* <a href="https://www.mozilla.org/firefox/" target="_blank">Mozilla Firefox</a> or <a href="https://www.google.com/chrome/" target="_blank">Google Chrome</a> web browser
* _PREFERRED:_ Familiarity with AWS <a href="https://aws.amazon.com/cli" target="_blank">CLI</a>, Management Console (EC2, RDS, VPC, CloudWatch), and basic SQL commands.

## Use the provided temporary AWS accounts

This workshop uses **AWS Event Engine**, a tool that dispenses individual workshop participants with a unique 12-digit alphanumeric code. This code should have been provided to you upon entry or beginning of the workshop, and it allows you to use a separate lab environment AWS account, without requiring the need for you to run this on your own personal or business accounts.

If you have not received the code, please reach out to one of our support staff at the workshop.

Go to <a href="https://dashboard.eventengine.run/" target="_blank">**https://dashboard.eventengine.run/**</a> (open a new browser tab), enter the access code and click **Proceed**.

<span class="image">![EventEngine Login](ee-login.png?raw=true)</span>

On the **User Dashboard**, please click **AWS Console** to log into the AWS Management Console.

<span class="image">![EventEngine Dashboard](ee-dashboard.png?raw=true)</span>

Click **Open AWS Console**. For the purposes of this workshop, you will not need to use command line and API access credentials.

<span class="image">![EventEngine Open Console](ee-open-console.png?raw=true)</span>

## Conventions

Due to the multi-region nature of this workshop, you will often be switching between the two regions that has been assigned to you. You can always confirm and change the region on the top of the AWS Console Navigation Menu. __Please be mindful__ that you are performing the actions in the proper region, as some of the resources created are very similar between the two regions. The instructions will clearly label the AWS Region in which you will be performing the actions in, as indicated by these unique header labels when switching:

> **`Region 1 (Primary)`**    &nbsp;&nbsp;&nbsp;&nbsp;and&nbsp;&nbsp;&nbsp;&nbsp;    **`Region 2 (Secondary)`**

<span class="image">![Console Region Change](region-change.png)</span>

We will also provide commands for you to run in the terminal <a href="https://aws.amazon.com/systems-manager/features/#Session_Manager" target="_blank">AWS Systems Manager Session Manager</a>. These commands will look like this, with <b><i>highlighted text</i></b> usually replaced by values that are unique to your account settings and resource names:

<pre>
$ ssh -i <b><i>PRIVATE_KEY.PEM</i></b> ec2-user@<b><i>EC2_PUBLIC_DNS_NAME</i></b>
</pre>

You will often also see some sections that are expandable/collapsible to make the instructions more readable:

<details>
<summary><b>Click here to expand!</b></summary>
Good job! You expanded for more details! Click again to hide/collapse.
</details>

## Overview of labs

* AWS Experience: Intermediate
* Time to Complete: 75-100 minutes

We will run the following modules, starting with the [setup](setup/index.md).

\# | Lab Module |  Overview
--- | --- | ---
1 | [**Setup**](setup/index.md) | Creating a Multi-Region workshop environment using AWS CloudFormation
2 | [**Create Global Database**](gdb/index.md) | Create Aurora Global Database from existing Aurora DB cluster
3 | [**Connect Application**](biapp/index.md) | Connect BI applications; Global Database in Action
4 | [**Monitor Latency**](cw/index.md) | Use CloudWatch to monitor for latency
5 | [**Failover**](failover/index.md) | Failover to the second region / simulate a regional failure and DR scenario
6 | [**Failback**](failback/index.md) | Optional - Failback to original region.
7 | **Decommission** | Not Required for Event Engine

## Workshop environment at a glance

To ensure everyone has a consistent experience, we have created foundational templates for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provisions the resources needed for the workshop environment on both regions.


![Workshop Architecture Diagram](summary-arch.png)

*	a <a href="https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html" target="_blank">Amazon VPC</a> network configuration with public and private subnets, NAT Gateway, Security Groups, etc.
*	a <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html#USER_VPC.Subnets" target="_blank">Database subnet group</a> and relevant <a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html" target="_blank">security groups</a> for the cluster and workstation
*	a <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Instances.html" target="_blank">Amazon EC2 instance</a> configured with the software components needed for the lab
*	<a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html" target="_blank">IAM roles</a> with access permissions for the workstation and cluster permissions for <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html" target="_blank">enhanced monitoring</a>, S3 access and logging
*	Custom cluster and DB instance <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithParamGroups.html" target="_blank">parameter groups</a> for the Amazon Aurora cluster, enabling logging and performance schema
*	an <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html" target="_blank">Amazon Aurora</a> MySQL DB cluster on the Primary Region

We will also be using the following services throughout the workshop:

*   <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html" target="_blank">AWS Systems Manager</a> Session Manager to gain shell access to the EC2 instance
*   <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html" target="_blank">Amazon CloudWatch</a> metrics and dashboards to monitor and report our Aurora Global Database replication lag


## Other relevant re:Invent 2019 Workshops

Want more? If you wish to attend other related Aurora or globally distributed architecture workshops, please look into your event catalog schedule for the following:

* DAT327-R / DAT327-R1 - Accelerating application development with Amazon Aurora (Workshop)
* ARC317-R / ARC317-R1 - Building global applications that align to BC/DR objectives (Workshop)
