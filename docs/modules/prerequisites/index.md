# Prerequisites

The following steps should be completed before getting started with any of the labs in this repository. Not all steps may apply to all students or environments.

This lab contains the following tasks:

1. Signing in to the AWS Management Console and creating an EC2 key pair
2. Creating a lab environment using AWS CloudFormation
3. Installing an SSH client (Windows Users)


## 1. Signing in to the AWS Management Console and creating an EC2 Key Pair

If you are running these labs in a formal, instructional setting, please use the Console URL, and credentials provided to you to access and log into the AWS Management Console. Otherwise, please use your own credentials. You can access the console at: <a href="https://console.aws.amazon.com/" target="_blank">https://console.aws.amazon.com/</a> or through the Single Sign-On (SSO) mechanism provided by your organization.

<span class="image">![AWS Management Console Login](./1-login.png?raw=true)</span>

If you are running these labs in a formal, instructional setting, please use the AWS region provided. Ensure the correct AWS region is selected in the top right corner, if not use that dropdown to choose the correct region. The labs are designed to work in any of the regions where Amazon Aurora MySQL compatible is available. However, not all features and capabilities of Amazon Aurora may be available in all supported regions at this time.

<span class="image">![AWS Management Console Region Selection](./1-region-select.png?raw=true)</span>

Open the **Key Pairs** section of the <a href="https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#KeyPairs:sort=keyName" target="_blank">EC2 service console</a>.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Click **Create Key Pair**.

<span class="image">![EC2 Console - Create Key Pair](./1-create-keypair.png?raw=true)</span>

Give the key pair a recognizable name, such as `labkeys`, then click **Create** and download the file named `labkeys.pem` to your computer, save it in a memorable location, such as your desktop.  You will need this file later in the lab.


## 2. Creating a lab environment using AWS CloudFormation

To simplify the getting started experience with the labs, we have created foundational templates for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provision the resources needed for the lab environment. These templates are designed to deploy a consistent networking infrastructure, and client-side experience of software packages and components used in the lab.

Please download the most appropriate CloudFormation template based on the labs you want to run:

Option | Download Template | One-Click Launch | Description
--- | --- | --- | ---
**I will create the DB cluster manually** | [lab-no-cluster.yml](https://[[website]]/templates/lab-no-cluster.yml) | <a href="https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=labstack&templateURL=https://s3.amazonaws.com/[[bucket]]/templates/lab-no-cluster.yml" target="_blank"><img src="/assets/images/cloudformation-launch-stack.png" alt="Launch Stack"></a> | Use when you wish to provision the initial cluster manually by following [Lab 1. - Creating a New Aurora Cluster](../create/)
**Provision the DB cluster for me** | [lab-with-cluster.yml](https://[[website]]/templates/lab-with-cluster.yml) | <a href="https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/new?stackName=labstack&templateURL=https://s3.amazonaws.com/[[bucket]]/templates/lab-with-cluster.yml" target="_blank"><img src="/assets/images/cloudformation-launch-stack.png" alt="Launch Stack"></a> | Use when you wish to skip the initial cluster creation lab, and have the DB cluster provisioned for you, so you can continue from [Lab 2. - Cluster Endpoints and Read Replica Auto Scaling](../connect/)

If you downloaded the template, save it in a memorable location such as your desktop, you will need to reference it later.

Open the <a href="https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks" target="_blank">CloudFormation service console</a>.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

Click **Create Stack**.

!!! note
    The CloudFormation console has been upgraded recently. Depending on your previous usage of the CloudFormation console UI, you may see the old design or the new design, you may also be presented with a prompt to toggle between them. In this lab we are using the new design for reference, although the steps will work similarly in the old console design as well, if you are more familiar with it.

<span class="image">![Create Stack](./2-create-stack.png?raw=true)</span>

Select the radio button named **Upload a template**, then **Choose file** and select the template file you downloaded previously named and then click **Next**.

<span class="image">![Upload Template](./2-upload-template.png?raw=true)</span>

In the field named **Stack Name**, enter the value `labstack`, for the **ec2KeyPair** parameter value input the name of the key pair you have created previously (`labkeys`) and then click **Next**. For the **vpcAZs** parameter select 3 availability zones (AZs) from the dropdown. If your desired region only supports 2 AZs, please select just the two AZs available.

<span class="image">![Configure Stack Options](./2-stack-params.png?raw=true)</span>

On the **Configure stack options** page, leave the defaults as they are, scroll to the bottom and click **Next**.

<span class="image">![Advanced Options](./2-no-advanced-opts.png?raw=true)</span>

On the **Review labstack** page, scroll to the bottom, check the box that reads: **I acknowledge that AWS CloudFormation might create IAM resources with custom names** and then click **Create**.

<span class="image">![Review Stack Options](./2-review-stack.png?raw=true)</span>

The stack will take approximatively 20 minutes to provision, you can monitor the status on the **Stack detail** page. You can monitor the progress of the stack creation process by refreshing the **Events** tab. The latest event in the list will indicate `CREATE_COMPLETE` for the stack resource.

<span class="image">![Stack Status](./2-stack-status.png?raw=true)</span>

Once the status of the stack is `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter format: ==[outputKey]==

<span class="image">![Stack Outputs](./2-stack-outputs.png?raw=true)</span>


## 3. Installing an SSH client (Windows Users)

Windows users: please download **PuTTY** `putty.exe` and the **PuTTY Key Generator** `puttygen.exe` from the following links, if you do not already have a SSH client available.

* <a href="https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe" target="_blank">PuTTY</a>
* <a href="https://the.earth.li/~sgtatham/putty/latest/w64/puttygen.exe" target="_blank">PuTTY Key Generator</a>

Once you have downloaded the client software, open `puttygen.exe` and click on **Load**.

::TODO Screenshot::

Please make sure that the file filter is set to `All Files (*.*)` and then select the EC2 Key Pair created earlier `labkeys.pem`.

::TODO Screenshot::

Fill in the **Key passphrase** and **Confirm passphrase** fields with a password of your choice that will be used to encrypt your private key and then click **Save private key**.  Please use the same name `labkeys.ppk` as your new key name.

::TODO Screenshot::

Next, open `putty.exe` and enter into the **Host Name (or IP address)** field the value of your bastion host generated from the AWS CloudFormation template that you used to bootstrap the labs:

```
ubuntu@[bastionEndpoint]
```

::TODO Screenshot::

Next, navigate within PuTTY to **Connection > SSH > Auth** and browse to the `labkeys.ppk` file that you created with the **PuTTY Key Generator** previously, and then click **Open**.

::TODO Screenshot::

When prompted by the **PuTTY Security Alert**, click **Yes**.

::TODO Screenshot::

Next, enter the password that you configured when you created the `labkeys.ppk` private file previously.

::TODO Screenshot::
