# Cloning Clusters

This lab will walk you through the process of <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Managing.Clone.html" target="_blank">cloning a DB cluster</a>. Cloning creates a separate, independent DB cluster, with a consistent copy of your data set as of the time you cloned it. Database cloning uses a copy-on-write protocol, in which data is copied at the time that data changes, either on the source databases or the clone databases. The two clusters are isolated, and there is no performance impact on the source DB cluster from database operations on the clone, or the other way around.

This lab contains the following tasks:

1. Creating a clone DB cluster
2. Verifying that the data set is identical
3. Changing data on the clone
4. Verifying that the data diverges


## 1. Creating a clone DB cluster

!!! warning "Workload State Check"
    Before cloning the DB cluster ensure you have stopped any load generating tasks from the previous lab, and exited out of the MySQL client command line using `quit;`.

On the EC2-based workstation you [connected to in the previous lab](/modules/connect/#1-connecting-to-your-workstation-ec2-instance), enter:

```
aws rds restore-db-cluster-to-point-in-time --restore-type copy-on-write --use-latest-restorable-time --source-db-cluster-identifier [clusterName] --db-cluster-identifier [clusterName]-clone --vpc-security-group-ids [dbSecurityGroup] --db-subnet-group-name [dbSubnetGroup] --backtrack-window 86400
```

You can find the parameter values for the ==[placeholders]== above in the Outputs section of the CloudFormation stack you deployed when [completing the prerequisites](/modules/prerequisites/#2-creating-a-lab-environment-using-aws-cloudformation). If you have opted to create the DB cluster manually, use the DB cluster identifier you have configured when [creating the Aurora DB cluster](/modules/create/) for the ==[clusterName]== placeholder.

Next, check the status of the creation of your clone, by using the following command. The cloning process can take several minutes to complete. See the example output below.

```
aws rds describe-db-clusters --db-cluster-identifier [clusterName]-clone
```

Take note of both the ==Status== and the ==Endpoint== attributes of the command output. Once the **Status** becomes **available**, you can add a DB instance to the cluster and once the DB instance is added, you will want to connect to the cluster via the **Endpoint** value, which represents the cluster endpoint.

<span class="image">![DB Cluster Status](1-describe-cluster.png?raw=true)</span>

!!! note
    Creating a DB cluster clone, even without adding DB instances, can be a useful and cost effective safety net measure, if you are about to make significant changes to your source cluster (such as an upgrade or risky DDL operation). The clone then becomes a quick rollback target, in case you encounter issues on the source as a result of the operation. You simply add a DB instance and point your application to the clone in such an event. We do not recommend using clones as long term point in time snapshot tools, as you are limited to 15 clones derived directly or indirectly from the same source.


Add a DB instance to the cluster once the status of the cluster becomes **available**, using the following command:

```
aws rds create-db-instance --db-instance-class db.r5.large --engine aurora --db-cluster-identifier [clusterName]-clone --db-instance-identifier [clusterName]-clone-instance
```

Check the creation of the DB instance within the cluster, by using the following command:

```
aws rds describe-db-instances --db-instance-identifier [clusterName]-clone-instance
```

<span class="image">![DB Instance Status](1-describe-instance.png?raw=true)</span>

Repeat the command to monitor the creation status. Once the ==DBInstanceStatus== attribute changes from **creating** to **available**, you have a functioning clone. Creating a node in a cluster also takes several minutes.

Next, connect to the instance using the following command (use the endpoint you retrieved from the `describe-db-cluster` command above):

```
mysql -h [cluster endpoint of clone] -u [username] -p [database]
```

If you have opted to create the DB cluster using CloudFormation, you can use the following command instead:

```
mysql -h [cluster endpoint of clone] -u$DBUSER -p"$DBPASS" mylab
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
--- | --- | --- | --- | ---
-h | [cluster endpoint of clone] | See above | See above | The cluster endpoint of the Aurora cloned DB cluster.
-u | [username] | `$DBUSER` | `masteruser` or manually set | The user name of the MySQL user to authenticate as.
-p | [password] | `$DBPASS` | Manually set, enter when prompted | The password of the MySQL user to authenticate as.
| [database] | `mylab` | `mylab` or manually set | The schema (database) to use by default.

!!! note
    The database credentials you use to connect are the same as for the source DB cluster, as this is an exact clone of the source.

## 2. Verifying that the data set is identical

Verify that the data set is identical on both the source and cloned DB clusters, before we make any changes to the data. You can verify by performing a checksum operation on the **sbtest1** table.

Since you are already connected to the cloned DB cluster, issue the following command there first:

```
checksum table sbtest1;
```

The output of your commands should look similar to the example below. Please take note of the value for your specific clone cluster.

<span class="image">![Checksum on clone](2-checksum-clone.png?raw=true)</span>

Now disconnect from the clone and connect to the source cluster with the following sequence:

```
quit;

mysql -h [clusterEndpoint] -u [username] -p [database]
```

If you have opted to create the DB cluster using CloudFormation, you can use the following command instead:

```
quit;

mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```


Execute the same checksum command that you ran on the clone:

```
checksum table sbtest1;
```

Please take note of the value for your specific source cluster. The checksum value should be the same as for the cloned cluster above.

## 3. Changing data on the clone

Disconnect from the original cluster (if you are still connected to it) and connect to the clone cluster with the following sequence:

```
quit;

mysql -h [cluster endpoint of clone] -u [username] -p [database]
```

If you have opted to create the DB cluster using CloudFormation, you can use the following command instead:

```
quit;

mysql -h [cluster endpoint of clone] -u$DBUSER -p"$DBPASS" mylab
```

Delete a row of data and execute the checksum command again:

```
delete from sbtest1 where id = 1;

checksum table sbtest1;
```

The output of your commands should look similar to the example below. Notice that the checksum value changed, and is no longer the same as calculated in section 2 above.

<span class="image">![Checksum on clone changed](3-checksum-clone-changed.png?raw=true)</span>

## 4. Verifying that the data diverges

Verify that the checksum value did not change on the source cluster as a result of the delete operation on the clone. Disconnect from the clone (if you are still connected) and connect to the source cluster with the following sequence:

```
quit;

mysql -h [clusterEndpoint] -u [username] -p [database]
```

If you have opted to create the DB cluster using CloudFormation, you can use the following command instead:

```
quit;

mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```

Execute the same checksum command that you ran on the clone:

```
checksum table sbtest1;
```

Please take note of the value for your specific source cluster. The checksum value should be the same as calculated for the source cluster above in section 2.
