# Prerequisites

The following steps should be completed before getting started with any of the labs in this repository. Not all steps may apply to all students or environments.

1. Sign in to the AWS Management Console, Select Region and Create Key Pair
2. Create a lab environment using AWS CloudFormation
3. Install an SSH client (Windows Users)


## 1. Sign in to the AWS Management Console, Select Region and Create Key Pair

1. If you are running these labs in a formal, instructional setting, please use the Console URL, and credentials provided to you to access and log into the AWS Management Console. Otherwise, please use your own credentials. You can access the console at: <a href="https://console.aws.amazon.com/" target="_blank">https://console.aws.amazon.com/</a> or through the Single Sign-On (SSO) mechanism provided by your organization.

    <span class="image">![AWS Management Console Login](./1.1-login.png?raw=true)</span>

2. If you are running these labs in a formal, instructional setting, please use the AWS region provided. Ensure the correct AWS region is selected in the top right corner, if not use that dropdown to choose the correct region. The labs are designed to work in any of the regions where Amazon Aurora MySQL compatible is available. However, not all features and capabilities of Amazon Aurora may be available in all supported regions at this time.

    <span class="image">![AWS Management Console Region Selection](./1.2-region-select.png?raw=true)</span>

3. Open the **Key Pairs** section of the <a href="https://us-west-2.console.aws.amazon.com/ec2/v2/home?region=us-west-2#KeyPairs:sort=keyName" target="_blank">EC2 service console</a>.

    !!! warning "Region Check"
        Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

4. Click **Create Key Pair**.

    <span class="image">![EC2 Console - Create Key Pair](./1.4-create-keypair.png?raw=true)</span>

5. Give the key pair a recognizable name, such as `labkeys`, then click **Create** and download the file named `labkeys.pem` to your computer, save it in a memorable location, such as your desktop.  You will need this file later in the lab.


## 2. Create a lab environment using AWS CloudFormation
To simplify the getting started experience with the labs, we have created foundational templates for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provision the resources needed for the lab environment. These templates are designed to deploy a consistent networking infrastructure, and client-side experience of software packages and components used in the lab.

The environment deployed using CloudFormation includes several components, as listed below. Please download the most appropriate CloudFormation template based on the labs you want to run.

*	<a href="https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html" target="_blank">Amazon VPC</a> network configuration with public and private subnets
*	<a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_VPC.WorkingWithRDSInstanceinaVPC.html#USER_VPC.Subnets" target="_blank">Database subnet group</a> and relevant <a href="https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html" target="_blank">security groups</a> for the cluster and workstation
*	<a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/Instances.html" target="_blank">Amazon EC2 instance</a> configured with the software components needed for the lab
*	<a href="https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html" target="_blank">IAM roles</a> with access permissions for the workstation and cluster permissions for <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_Monitoring.OS.html" target="_blank">enhanced monitoring</a>, S3 access and logging
*	Custom cluster and DB instance <a href="https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/USER_WorkingWithParamGroups.html" target="_blank">parameter groups</a> for the Amazon Aurora cluster, enabling logging and performance schema
*	Optionally, <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html" target="_blank">Amazon Aurora</a> DB cluster with 2 nodes: a writer and read replica
* If the cluster is created for you, the master database credentials will be generated automatically and stored in an <A href="https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html" target="_blank">AWS Secrets Manager</a> secret.
*	Optionally, <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Integrating.AutoScaling.html" target="_blank">read replica auto scaling</a> configuration
*	Optionally, <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html" target="_blank">AWS Systems Manager</a> command document to execute a load test

The following templates are available:

* [**lab-no-cluster.yml**](../../templates/lab-no-cluster.yml?raw=true) - use when you wish to provision the initial cluster manually by following [Lab 1. - Creating a New Aurora Cluster](../create/)
* [**lab-with-cluster.yml**](../../templates/lab-with-cluster.yml?raw=true) - use when you wish to skip the initial cluster creation lab, and have it provisioned for you, so you can continue from [Lab 2. - Cluster Endpoints and Read Replica Auto Scaling](../connect/)

Create the lab environment by following the steps below:

1. Download the most suitable CloudFormation template listed above. Save it in a memorable location such as your desktop, you will need to reference it later.

2. Open the <a href="https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks" target="_blank">CloudFormation service console</a>.

    !!! warning "Region Check"
        Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

4. Click **Create Stack**.

    !!! note
        The CloudFormation console has been upgraded recently. Depending on your previous usage of the CloudFormation console UI, you may see the old design or the new design, you may also be presented with a prompt to toggle between them. In this lab we are using the new design for reference, although the steps will work similarly in the old console design as well, if you are more familiar with it.

    <span class="image">![Create Stack](./2.0-create-stack.png?raw=true)</span>

4. Select the radio button named **Upload a template**, then **Choose file** and select the template file you downloaded previously named and then click **Next**.

    <span class="image">![Upload Template](./2.1-upload-template.png?raw=true)</span>

5. In the field named **Stack Name**, enter the value `labstack`, for the **ec2KeyPair** parameter value input the name of the key pair you have created previously (`labkeys`) and then click **Next**. For the **vpcAZs** parameter select 3 availability zones (AZs) from the dropdown. If your desired region only supports 2 AZs, please select just the two AZs available.

    <span class="image">![Configure Stack Options](./2.2-stack-params.png?raw=true)</span>

6. On the **Configure stack options** page, leave the defaults as they are, scroll to the bottom and click **Next**.

    <span class="image">![Advanced Options](./2.3-no-advanced-opts.png?raw=true)</span>

7. On the **Review labstack** page, scroll to the bottom, check the box that reads: **I acknowledge that AWS CloudFormation might create IAM resources with custom names** and then click **Create**.

    <span class="image">![Review Stack Options](./2.4-review-stack.png?raw=true)</span>

8. The stack will take approximatively 20 minutes to provision, you can monitor the status on the **Stack detail** page. You can monitor the progress of the stack creation process by refreshing the **Events** tab. The latest event in the list will indicate `CREATE_COMPLETE` for the stack resource.

    <span class="image">![Stack Status](./2.5-stack-status.png?raw=true)</span>

9. Once the status of the stack is `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter format: ==[outputKey]==

    <span class="image">![Stack Outputs](./2.6-stack-outputs.png?raw=true)</span>


## 3. Install an SSH client (Windows Users)

Windows users: please download **PuTTY** `putty.exe` and the **PuTTY Key Generator** `puttygen.exe` from the following links, if you do not already have a SSH client available.

* <a href="https://the.earth.li/~sgtatham/putty/latest/w64/putty.exe" target="_blank">PuTTY</a>
* <a href="https://the.earth.li/~sgtatham/putty/latest/w64/puttygen.exe" target="_blank">PuTTY Key Generator</a>

Use the following steps to configure PuTTY:

1. Once you have downloaded the client software, open `puttygen.exe` and click on **Load**.

2. Please make sure that the file filter is set to `All Files (*.*)` and then select the EC2 Key Pair created earlier `labkeys.pem`.

3. Fill in the **Key passphrase** and **Confirm passphrase** fields with a password of your choice that will be used to encrypt your private key and then click **Save private key**.  Please use the same name `labkeys.ppk` as your new key name.

4. Next, open `putty.exe` and enter into the **Host Name (or IP address)** field the value of your bastion host generated from the AWS CloudFormation template that you used to bootstrap the labs:

    `ubuntu@[bastionEndpoint]`

5. Next, navigate within PuTTY to **Connection > SSH > Auth** and browse to the `labkeys.ppk` file that you created with the **PuTTY Key Generator** previously, and then click **Open**.

6. When prompted by the **PuTTY Security Alert**, click **Yes**.

7. Next, enter the password that you configured when you created the `labkeys.ppk` private file previously.
