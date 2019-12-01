# Manual Deployment for Primary Region <span style="color:red;">(only for testing or if Autodeploy failed)

* On the upper right corner of the AWS Console, click on the region and select your primary region assigned to you.

> **`Region 1 (Primary)`**

| Region 1 | Region 1 Location | Deploy |
| --- | --- | --- |
| us-east-1 | N. Virginia |  <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/create/review?stackName=gdb1&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb1-with-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Primary"></a> |
| us-east-2 | Ohio | <a href="https://console.aws.amazon.com/cloudformation/home?region=us-east-2#/stacks/create/review?stackName=gdb1&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb1-with-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Primary"></a> |
| us-west-2 | Oregon | <a href="https://console.aws.amazon.com/cloudformation/home?region=us-west-2#/stacks/create/review?stackName=gdb1&templateURL=https://s3.amazonaws.com/ams-labs-prod-content-us-east-1/templates/lab-gdb1-with-cluster.yml" target="_blank"><img src="../../assets/images/cloudformation-launch-stack.png" alt="Deploy - Primary"></a> |

* Choose the region above matching your assigned primary region to deploy the workshop environment. You can also download the [lab-gdb1-with-cluster.yml](/templates/lab-gdb1-with-cluster.yml) template and manually upload it to CloudFormation in your primary region.

* The desired template should be filled under **Template URL**. In the field named **Stack Name**, enter the value `gdb1`. For the **dbMasterPassword** parameter, leave the default password or enter a password for the Aurora database that you can remember for connecting later. Leave all other parameters as default.

* Scroll to the bottom, check the box that reads: **I acknowledge that AWS CloudFormation might create IAM resources with custom names** and then click **Create stack**.

  <span class="image">![Region 1 CFN Launch](setup-cfn-gdb1a.png)</span>

* The stack will take approximately 20 minutes to provision, you can monitor the status on the **Stack detail** page. You can monitor the progress of the stack creation process by refreshing the **Events** tab. The latest event in the list will indicate `CREATE_COMPLETE` for the stack resource.

  <span class="image">![Region 1 CFN Launch](setup-cfn-gdb1b.png)</span>

* Once the status of the stack is `CREATE_COMPLETE`, click on the **Outputs** tab. The values here will be critical to the completion of the remainder of the lab.  Please take a moment to save these values somewhere that you will have easy access to them during the remainder of the lab. The names that appear in the **Key** column are referenced directly in the instructions in subsequent steps, using the parameter value format: ``=[outputKey]=``

  <span class="image">![Region 1 CFN Launch](setup-cfn-gdb1c.png)</span>
  

* Return to the rest of [Setup](index.md)