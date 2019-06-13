# Using Performance Insights

::TODO:: Insert overview description here

## 1. Generating Load on your DB Cluster

You will use Percona's TPCC-like benchmark script based on sysbench to generate load. For simplicity we have packaged the correct set of commands in an AWS Systems Manager Command Document. You will use AWS Systems Manager Run Command to execute the test.

1. On the workstation host, execute the following statement:

    `aws ssm send-command --document-name [loadTestRunDoc] --instance-ids [bastionInstance]`

2. The command will be sent to the workstation EC2 instance which will prepare the test data set and run the load test. It may take up to a minute for CloudWatch to reflect the additional load in the metrics.

## 2. Examining the Performance of your DB instance

1.	Navigate to the RDS service console (http://bit.ly/dat312-rds) and click on Performance Insights in the left side navigation bar.

::TODO:: add more instructions
