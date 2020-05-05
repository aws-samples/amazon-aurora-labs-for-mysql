# Deploying an Aurora Global Database




This lab contains the following tasks:

1. Create a lab environment in a different region
2. Generate load on your DB cluster
3. Create an Aurora Global cluster
4. Add a secondary region to the global cluster
5. Monitor cluster load and replication lag
6. Promote the secondary region

This lab requires the following prerequisites:

* [Get Started](/win/)
* [Connect to your Aurora MySQL DB cluster](/win/ams-connect/)


## 1. Create a lab environment in a different region

To simplify the getting started experience with the labs, we have created foundational templates for <a href="https://aws.amazon.com/cloudformation/" target="_blank">AWS CloudFormation</a> that provision the resources needed for the lab environment. These templates are designed to deploy a consistent networking infrastructure, and client-side experience of software packages and components used in the lab.

Click **Launch Stack** below to provision a lab environment in the **N Virginia (us-east-1)** region to support the Aurora Global Database.

<a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?stackName=labstack&templateURL=https://s3.amazonaws.com/[[bucket]]/templates/lab_template.yml&param_deployCluster=No&param_deployML=No" target="_blank"><img src="/assets/images/cloudformation-launch-stack.png" alt="Launch Stack"></a>

In the field named **Stack Name**, ensure the value `labstack` is preset. Accept all default values for the remaining parameters.

Scroll to the bottom of the page, check the box that reads: **I acknowledge that AWS CloudFormation might create IAM resources with custom names** and then click **Create stack**.

<span class="image">![Create Stack](2-create-stack-confirm.png?raw=true)</span>

The stack will take approximatively 10 minutes to provision, you can monitor the status on the **Stack detail** page. You can monitor the progress of the stack creation process by refreshing the **Events** tab. The latest event in the list will indicate `CREATE_COMPLETE` for the stack resource.

<span class="image">![Stack Status](2-stack-status.png?raw=true)</span>

Once the status of the stack is `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter format: ==[outputKey]==

<span class="image">![Stack Outputs](2-stack-outputs.png?raw=true)</span>


## 2. Generate load on your DB cluster

While the second region is being built up, you will use Percona's TPCC-like benchmark script based on sysbench to generate load on the DB cluster in the existing region. For simplicity we have packaged the correct set of commands in an <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-ssm-docs.html" target="_blank">AWS Systems Manager Command Document</a>. You will use <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/execute-remote-commands.html" target="_blank">AWS Systems Manager Run Command</a> to execute the test. The load generator will run for approximatively one hour.

If you are not already connected to the Session Manager workstation command line, please connect [following these instructions](/win/ams-connect/). Once connected, enter one of the following commands, replacing the placeholders appropriately.

```shell
aws ssm send-command \
--document-name [mysqlRunDoc] \
--instance-ids [bastionMySQL]
```

??? tip "What do all these parameters mean?"
    Parameter | Description
    --- | ---
    --document-name | The name of the command document to run on your behalf.
    --instance-ids | The EC2 instance to execute this command on.

The command will be sent to the workstation EC2 instance which will prepare the test data set and run the load test. It may take up to a minute for CloudWatch to reflect the additional load in the metrics. You will see a confirmation that the command has been initiated.

<span class="image">![SSM Command](1-ssm-command.png?raw=true)</span>

## 3. Create an Aurora Global cluster
