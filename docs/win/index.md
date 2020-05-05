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

## Get the environment parameters

Once you have opened the AWS Management Console for the first time, go ahead and open the <a href="https://eu-west-1.console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks" target="_blank">AWS CloudFormation</a> console and click on the `labstack` stack.

::TODO:: Screenshot

If the status of the stack is `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter format: ==[outputKey]==

<span class="image">![Stack Outputs](stack-outputs.png?raw=true)</span>

## Start the labs

For your convenience, a lab environment has already been deployed for you. The lab environment contains the following resources:

1. **Two Amazon Aurora database clusters**, one running PostgreSQL, the other running MySQL. They are named **labstack-postgres-cluster** and **labstack-mysql-cluster**. Each DB cluster contains two database instances (with names ending in node-1 and node-2), deployed each in two separate Availability Zones for Multi-AZ high availability. One of the DB instances is a writer (master), the other a reader (read-only replica).
2. **Two EC2-based workstations**, one containing the necessary software to complete the Aurora PostgreSQL labs, the other to be used for the Aurora MySQL labs. You will connect to them using <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html" target="_blank">AWS Systems Manager</a> - Session Manager, following the instructions provided. You do not need to install any client software on your computer.
3. Supporting resources and network configuration, including: <a href="https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html" target="_blank">VPC</a>, subnets, gateways, subnet groups, security groups, IAM roles, credentials stored in an <a href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html" target="_blank">AWS Secrets Manager</a> secret.

Time permitting, you will run the following hands-on labs. Start with  [connecting to Aurora PostgreSQL](/win/apg-connect/).

# | Lab Module | Recommendation | Overview
--- | --- | --- | ---
1 | [**Connect to Aurora PostgreSQL**](/win/apg-connect/) | Connect to the lab environment for the Aurora PostgreSQL labs.
2 | [**Use Query Plan Management**](/win/apg-qpm/) | Learn how to use the query plan management features of Aurora PostgreSQL.
3 | [**Set up Database Activity Streams**](/win/apg-das/) |
4 | [**Connect to Aurora MySQL**](/win/ams-connect/) | Connect to the DB cluster for the first time and load an initial data set
5 | [**Clone an Aurora DB cluster**](/win/ams-clone/) | Clone an Aurora DB cluster and observing the divergence of the data set.
6 | [**Deploy a Global Database**](/win/ams-gdb) |
7 | [**Create a Serverless DB cluster**](/win/ams-srvless-create/) | Optional. Connect to your serverless cluster using the RDS Data API and Lambda functions.
8 | [**Use the RDS Data API**](/win/ams-srvless-data-api/) | Optional. Connect to your serverless cluster using the RDS Data API and Lambda functions. Requires the previous lab.
