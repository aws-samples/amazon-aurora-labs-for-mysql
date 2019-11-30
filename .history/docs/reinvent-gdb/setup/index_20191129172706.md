# Setup - Creating a Multi-Region workshop environment using AWS CloudFormation

To simplify the getting started experience with the labs, we have created foundational templates for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provisions the resources needed for the lab environment. The template is designed to deploy a consistent networking infrastructure, and client-side experience of software packages and components used in the workshop.


## Workshop Setup - Primary Region

If you are at re:Invent or an AWS public event, you are likely provided a 12-digit team code that gives access to a temporary AWS account dedicated for this workshop. If that is the case, the accounts already have the infrastructure in the assigned primary region pre-deployed.

> **`Region 1 (Primary)`**

1. In the AWS Management Console, ensure that you are working within your assigned primary region. Using the Service menu, click on or type to search for **CloudFormation**. This will bring up the Amazon CloudFormation console.

1. On the next screen, click on the stack with the Description *Amazon Aurora Labs - Global Database Workshop (Region 1)*, you should see that the status shows *CREATE_COMPLETE*.

1. Click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter value format: ``=[outputKey]=``

4. This confirms that we have resources ready in the primary region. We can skip steps below and go directly to **Workshop Setup - Secondary Region**.

<details>
<summary><b>Manual Deployment for Primary Region <span style="color:red;">(expand only for testing or if Stack was missing)</span></b></summary>

On the upper right corner of the AWS Console, click on the region and select your primary region assigned to you.

> **`Region 1 (Primary)`**

| Region | Region Location | Deploy |
| --- | --- | --- |
| us-east-1 | N. Virginia |  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?stackName=gdb1&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb1-with-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Primary"></a> |
| us-east-2 | Ohio | <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/create/review?stackName=gdb1&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb1-with-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Primary"></a> |
| us-west-2 | Oregon | <a href="https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?stackName=gdb1&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb1-with-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Primary"></a> |
| ap-southeast-1 | Singapore | <a href="https://console.aws.amazon.com/cloudformation/home?region=ap-southeast-1#/stacks/create/review?stackName=gdb1&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb1-with-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Primary"></a> |
| ap-southeast-2 | Sydney | <a href="https://console.aws.amazon.com/cloudformation/home?region=ap-southeast-2#/stacks/create/review?stackName=gdb1&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb1-with-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Primary"></a> |

Choose the region above matching your assigned primary region to deploy the workshop environment. You can also download the [lab-gdb1-with-cluster.yml](/templates/lab-gdb1-with-cluster.yml) template and manually upload it to CloudFormation in your primary region.

The desired template should be filled under **Template URL**. In the field named **Stack Name**, enter the value `gdb1`. For the **dbMasterPassword** parameter, leave the default password or enter a password for the Aurora database that you can remember for connecting later. Leave all other parameters as default.

Scroll to the bottom, check the box that reads: **I acknowledge that AWS CloudFormation might create IAM resources with custom names** and then click **Create stack**.

<span class="image">![Region 1 CFN Launch](setup-cfn-gdb1a.png)</span>

The stack will take approximatively 20 minutes to provision, you can monitor the status on the **Stack detail** page. You can monitor the progress of the stack creation process by refreshing the **Events** tab. The latest event in the list will indicate `CREATE_COMPLETE` for the stack resource.

<span class="image">![Region 1 CFN Launch](setup-cfn-gdb1b.png)</span>

Once the status of the stack is `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter value format: ``=[outputKey]=``

<span class="image">![Region 1 CFN Launch](setup-cfn-gdb1c.png)</span>

</details>

## Workshop Setup - Secondary Region

On the upper right corner of the AWS Console, click on your existing secondary region name and switch over to the secondary region that is assigned to you.

> **`Region 2 (Secondary)`**

| Region | Region Location | Deploy |
| --- | --- | --- |
| us-east-1 | N. Virginia |  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?stackName=gdb2&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb2-no-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Secondary"></a> |
| us-east-2 | Ohio | <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/create/review?stackName=gdb2&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb2-no-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Secondary"></a> |
| us-west-2 | Oregon | <a href="https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?stackName=gdb2&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb2-no-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Secondary"></a> |
| ap-southeast-1 | Singapore | <a href="https://console.aws.amazon.com/cloudformation/home?region=ap-southeast-1#/stacks/create/review?stackName=gdb2&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb2-no-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Secondary"></a> |
| ap-southeast-2 | Sydney | <a href="https://console.aws.amazon.com/cloudformation/home?region=ap-southeast-2#/stacks/create/review?stackName=gdb2&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb2-no-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Secondary"></a> |

Choose the region above matching your assigned secondary region to deploy the workshop environment. You can also download the [lab-gdb2-no-cluster.yml](/templates/lab-gdb2-no-cluster.yml) template and manually upload it to CloudFormation in your secondary region.

**Important**: Remember your primary and secondary region should be different. Refer back to the regions that has been assigned to you if you forget.

The desired template should be filled under **Template URL**. In the field named **Stack Name**, enter the value `gdb2`.

Scroll to the bottom, check the box that reads: **I acknowledge that AWS CloudFormation might create IAM resources with custom names** and then click **Create stack**.

<span class="image">![Region 2 CFN Launch](setup-cfn-gdb2a.png)</span>

In about 2-3 minutes, the status of the stack will change to `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter value format: ``=[outputKey]=``

</details>

## Checkpoint

At this point, you should have the base resources provisioned in the following:

> **`Region 1 (Primary)`**

* Basic VPC with public and private subnets across 3 availability zones; security groups and NAT Gateway
* VPC NACLs (for failure injection)
* Amazon EC2 Instance with Apache Superset (Our BI Application)
* Amazon Aurora Regional Cluster
* Amazon RDS DB subnet group for Aurora

> **`Region 2 (Secondary)`**

* Basic VPC with public and private subnets across 3 availability zones; security groups and NAT Gateway
* Amazon EC2 Instance with Apache Superset (Our BI Application)
* Amazon RDS DB subnet group for Aurora

You should now have also gathered the CloudFormation **Outputs** values from both regions. Below is a architectural representation of the resources that has been deployed so far.

![Setup Architecture Diagram](setup-arch.png)
