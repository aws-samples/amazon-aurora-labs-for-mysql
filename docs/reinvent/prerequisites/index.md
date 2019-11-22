# Prerequisites

This lab contains the following tasks:

1. Creating a lab environment using AWS CloudFormation

## 1. Creating a lab environment using AWS CloudFormation

To simplify the getting started experience with the labs, we have created a foundational template for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provisions the resources needed for the lab environment. The template is designed to deploy a consistent networking infrastructure, and client-side experience of software packages and components used in the workshop.

<a href="https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/new?stackName=labstack&templateURL=https://s3.amazonaws.com/[[bucket]]/templates/lab-with-cluster.yml" target="_blank"><img src="/assets/images/cloudformation-launch-stack.png" alt="Launch Stack"></a>

Click <a href="https://console.aws.amazon.com/cloudformation/home?region=eu-west-1#/stacks/new?stackName=labstack&templateURL=https://s3.amazonaws.com/[[bucket]]/templates/lab-with-cluster.yml" target="_blank">Launch Stack</a> to deploy the workshop environment. You can also download the [lab-with-cluster.yml](https://[[website]]/templates/lab-with-cluster.yml) template and manually upload it to CloudFormation.

The desired template should be pre-selected under **Amazon S3 URL**, click **Next**.

<span class="image">![Upload Template](../../modules/prerequisites/2-select-template.png?raw=true)</span>

In the field named **Stack Name**, enter the value `labstack`. For the **vpcAZs** parameter select 3 availability zones (AZs) from the dropdown. Click **Next**.

<span class="image">![Configure Stack Options](../../modules/prerequisites/2-stack-params.png?raw=true)</span>

On the **Configure stack options** page, leave the defaults as they are, scroll to the bottom and click **Next**.

<span class="image">![Advanced Options](../../modules/prerequisites/2-no-advanced-opts.png?raw=true)</span>

On the **Review labstack** page, scroll to the bottom, check the box that reads: **I acknowledge that AWS CloudFormation might create IAM resources with custom names** and then click **Create**.

<span class="image">![Review Stack Options](../../modules/prerequisites/2-review-stack.png?raw=true)</span>

The stack will take approximatively 20 minutes to provision, you can monitor the status on the **Stack detail** page. You can monitor the progress of the stack creation process by refreshing the **Events** tab. The latest event in the list will indicate `CREATE_COMPLETE` for the stack resource.

<span class="image">![Stack Status](../../modules/prerequisites/2-stack-status.png?raw=true)</span>

Once the status of the stack is `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter format: ==[outputKey]==

<span class="image">![Stack Outputs](../../modules/prerequisites/2-stack-outputs.png?raw=true)</span>
