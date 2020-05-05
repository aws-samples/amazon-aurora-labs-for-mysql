# Connect to your Aurora PostgreSQL DB cluster

To interact with the Aurora database cluster, you will use an <a href="https://aws.amazon.com/ec2/" target="_blank">Amazon EC2</a> Linux instance that acts like a workstation to interact with the AWS resources in the labs on this website. All necessary software packages and scripts have been installed and configured on this EC2 instance for you. To ensure a unified experience, you will be interacting with this workstation using <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html" target="_blank">AWS Systems Manager Session Manager</a>. With Session Manager you can interact with your workstation directly from the management console, without the need to install any software on your own devices.

This lab contains the following tasks:

1. Note the CloudFormation resource chart
2. Retrieve database credentials from AWS Secret Manager
3. Connecting to the EC2 bastion instance with Systems Manager

This lab requires the following prerequisites:

* [Get Started](/win/)


## 1. Note the CloudFormation resource chart

At the end of the getting started step, you have retrieved the **Outputs** of your CloudFormation stack. For the following Aurora PostgreSQL labs, you will need the following values for lab resources:

Resource name | Value
--- | ---
Cluster Parameter Group | Refer to: ==[postgresClusterParamGroup]== in the stack outputs
Database Parameter Group | Refer to: ==[postgresNodeParamsGroup]== in the stack outputs
Cluster Endpoint | Refer to: ==[postgresClusterEndpoint]== in the stack outputs
Reader Endpoint	| Refer to: ==[postgresReaderEndpoint]== in the stack outputs
Secret Name	| Refer to: ==[secretArn]== in the stack outputs
DB name	| `mylab`
DB username	| `masteruser`
DB password	| See below for steps how to retrieve

## 2. Retrieve database credentials from AWS Secret Manager

1. Search for the secret name as shown in the output of the stack and select the secret name.

<span class="image">![1-qpm-secrets-1](1-qpm-secrets-1.png?raw=true)</span>

## 2. Click on the Retrieve secret value to get the Database user and the password to connect to the Aurora Database.

<span class="image">![1-qpm-secrets-2](1-qpm-secrets-2.png?raw=true)</span>

<span class="image">![1-qpm-secrets-3](1-qpm-secrets-3.png?raw=true)</span>

<span class="image">![1-qpm-secrets-4](1-qpm-secrets-4.png?raw=true)</span>

## 3. Connecting to the EC2 bastion instance with Systems Manager

Open the <a href="https://eu-west-1.console.aws.amazon.com/systems-manager/session-manager?region=eu-west-1" target="_blank">Systems Manager: Session Manager service console</a>.

<span class="image">![1-ssm1_1](../prerequisites/ssm1_1.png?raw=true)</span><br>

<span class="image">![1-ssm1_2](../prerequisites/ssm1_2.png?raw=true)</span><br>

Click **Start session**

<span class="image">![1-ssm1_3](../prerequisites/ssm1_3.png?raw=true)</span><br>

Click **Start session**

Select the instance named `labstack-postgres-bastion`, then click **Start session**.

<span class="image">![1-ssm1_4](../prerequisites/ssm1_4.png?raw=true)</span><br>

By default the system manager connects using the login **ssm-user**. You need to switch to the **ec2-user**:

```shell
sh-4.2$ whoami
ssm-user
sh-4.2$ sudo su -
Last login: Thu Feb 27 02:28:24 UTC 2020 on pts/1
[root@ip-x.x.x.x ~]# su - ec2-user
Last login: Wed Feb 26 18:04:46 UTC 2020 on pts/0
[ec2-user@x.x.x.x ~]$ whoami
ec2-user
```
<span class="image">![1-ssm1_5](../prerequisites/ssm1_5.png?raw=true)</span><br>
