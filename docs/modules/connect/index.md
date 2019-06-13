# Connecting, Loading Data and Auto Scaling

This lab will walk you through the process of connecting to the DB cluster you have just created, and using the cluster for the first time. At the end you will test out in practice how Aurora read replica auto scaling works in practice using a load generator script. This lab contains the following tasks:

1. Connecting to your workstation EC2 instance
2. Setting up the AWS CLI and connecting to the DB cluster
3. Loading an initial data set from S3
3. Running a read-only workload


## 1. Connecting to your workstation EC2 instance

For Windows users: We will use PuTTY and PuTTY Key Generator to connect to the workstation using SSH. If you do not have these applications already installed please use the instructions in the [Prerequisites](/modules/prerequisites/#3-install-an-ssh-client-windows-users) for setting up PuTTY and connecting via SSH.

For macOS or Linux users: You can connect using the following command from a terminal, however you will need to change the permissions of the certificate file first:

```
chmod 0600 /path/to/downloaded/labkeys.pem

ssh -i /path/to/downloaded/labkeys.pem ubuntu@[bastionEndpoint]
```


## 2. Setting up the AWS CLI and connecting to the DB cluster

1.	Enter the following command in the SSH console to configure the AWS CLI:

    `aws configure`

Then select the defaults for everything except the default region name.  For the default region name, enter "eu-west-1".

2.	Connect to the Aurora database using the following command:

mysql -h [clusterEndpoint] -u masteruser -p mylab

Unless otherwise specified the cluster master username is masteruser and the password is Password1

3.	Run the following queries on the database server, they will create a table, and load data from S3 into it:

DROP TABLE IF EXISTS `sbtest1`;
CREATE TABLE `sbtest1` (
 `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
 `k` int(10) unsigned NOT NULL DEFAULT '0',
 `c` char(120) NOT NULL DEFAULT '',
 `pad` char(60) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `k_1` (`k`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOAD DATA FROM S3 MANIFEST
's3-eu-west-1://aurorareinvent2018/output.manifest'
REPLACE
INTO TABLE sbtest1
CHARACTER SET 'latin1'
FIELDS TERMINATED BY ','
LINES TERMINATED BY '\r\n';



## PART 2. Cluster Endpoints and Auto Scaling

In this part we will explore the cluster endpoints and how auto scaling of read replicas operates.



### Task 2.1 - Running a read-only workload
1.	On the bastion host, execute the following statement:

python loadtest.py [readerEndpoint]

2.	Open the Amazon RDS service console located at: http://bit.ly/dat312-rds.

3.	Take note that the reader node is currently receiving load. It may take a minute or more for the metrics to fully reflect the incoming load.

4.	After a few minutes return to the list of instances and notice that a new reader is being provisioned to your cluster.

5.	Once the replicas are added, note that the load distributes and stabilizes.

6.	You can now type CTRL+C on the bastion host to end the read load, if you wish to. After a while the additional readers will be removed automatically.
