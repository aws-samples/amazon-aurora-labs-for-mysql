# Cloning Clusters

1.	On the bastion host, enter:

aws rds restore-db-cluster-to-point-in-time --restore-type copy-on-write --use-latest-restorable-time --source-db-cluster-identifier [clusterName] --db-cluster-identifier [clusterName]-clone --vpc-security-group-ids [dbSecurityGroup] --db-subnet-group-name [dbSubnetGroup] --backtrack-window 86400

2.	Next, to check the status of the creation of your clone, enter the following command on the bastion host. The cloning process can take several minutes to complete. See the example output below.

aws rds describe-db-clusters --db-cluster-identifier [clusterName]-clone

3.	Take note of both the "Status" and the "Endpoint."  Once the Status becomes available, you can add an instance to the cluster and once the instance is added, you will want to connect to the cluster via the Endpoint value.  To add an instance to the cluster once the status becomes available, enter the following:

aws rds create-db-instance --db-instance-class db.r4.large --engine aurora --db-cluster-identifier [clusterName]-clone --db-instance-identifier [clusterName]-clone-instance

4.	To check the creation of the instance, enter the following at the command line:

aws rds describe-db-instances --db-instance-identifier [clusterName]-clone-instance

5.	Once the DBInstanceStatus changes from creating to available, you have a functioning clone. Creating a node in a cluster also takes several minutes.

6.	Once your instance is created, connect to the instance using the following command:

mysql -h [cluster endpoint of clone cluster] -u masteruser -p mylab

Note: the master user account credentials will be the same as with the source of the cloned cluster. If you customized the CloudFormation template and changed the values, use the customized username and password.

7.	In order to verify that the clone is identical to the source, we will perform a checksum of the sbtest1 table using the following:

checksum table sbtest1;

8.	The output of your commands should look similar to the example below:

9.	Please take note of the value for your specific clone cluster.

10.	Next, we will disconnect from the clone and connect to the original cluster with the following:

quit;

mysql -h [clusterEndpoint] -u masteruser -p mylab

11.	Next, we will execute the same commands that we executed on the clone:

checksum table sbtest1;

12.	Please take note of the value for your specific source cluster. The checksum should be identical.
