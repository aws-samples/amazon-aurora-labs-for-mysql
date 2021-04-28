# Fail Back a Global Database

This is an optional lab. You will attempt to orchestrate the required operation to restore writable database access back in the primary region, after promoting the secondary DB cluster in the secondary region. You will only see high level instructions. Please take your time in first planning out the reverse/restore actions, and feel free to raise your hand (if you are at an AWS event) to share with us your questions, thoughts and ideas!

This lab contains the following tasks:

1. Overview of fail over and fail back in Amazon Aurora
2. End the simulated failure in the primary region
3. Build a new Global Database
4. Break the Global Database one more time
5. Rebuild the final Global Database
6. Delete the old secondary DB cluster
7. Summary

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/) (choose the **Deploy Global DB** option)
* [Connect to the Session Manager Workstation](/prereqs/connect/)
* [Deploy an Aurora Global Database](/global/deploy/)
* [Fail Over an Aurora Global Database](/global/failover/)


## 1. Overview of fail over and fail back in Amazon Aurora

As illustrated in the previous lab, **Global Database failover** is the process of shifting application and database resources from the original primary region to a secondary disaster recovery region during a large scale infrastructure or service level interruption. 

You may be able to design an application that is completely stateless and could be launched in any region, however the relational database tier, with Aurora Global Database, has one single writer DB instance, and it requires promotion of the secondary DB cluster in order for it to begin serving write requests. Changes are now only tracked on the DB cluster in the secondary region. This also required taking the secondary DB cluster out of the Aurora Global Database. The original Aurora Global Database remains, and replication continues with other secondary DB clusters in other regions if you have additional such extensions.

When the large scale interruption is restored, you usually want to restore the environment to its original setting, and synchronizing the original primary region to become the master node to serve write traffic, back again. This process is called **failback**, an operation that would see us returning production to its original location after the disaster event and all normal operations restored, while keeping track and capturing all the changed data that has been written to the recently-promoted secondary region. As the original primary region's DB cluster is now restored, you also want to avoid a *split-brain* scenario. 

To reiterate, for normal single-region scenarios, failover is automatic, and failback is usually unnecessary if the failover nodes are of the same instance family, type, and size. This also applies when the writer DB instance in the primary DB cluster of a Global Database fails. Failovers to other regions are typically not necessary in that case, as service is resotred automatically in the same region. Amazon Aurora DB clusters are available in AWS regions are resilient across multiple *Availability Zones*. This type of planning is only needed in the extremely unlikely scenario of failing over / failing back to a different region, because of a complete and likely longer time workload disruption in the primary region.


## 2. End the simulated failure in the primary region

You were previously simulating a large scale regional/service level interruption by associating a **Network ACL (NACL)** rule that denies all network traffic with the subnets where the Aurora Global Database primary DB cluster was deployed. Let's revert this to end the traffic block.

Go to your <a href="https://console.aws.amazon.com/vpc/home#acls:sort=networkAclId" target="_blank">VPC service console</a> in the **primary region** and remove the subnet associations from the NACL named **auroralab-denyall-nacl**. This will reconfigure the subnets to use the default NACL.

Since the data is now stale, and out of date compared to the secondary region Aurora DB cluster that was promoted, the Aurora DB cluster and DB instances in the primary region are no longer needed, for the purposes of the Global Database labs. Normally you would want to delete them, **but don't**. There may be other labs in your curriculum that depend on this DB cluster. 

You can however delete the global cluster, by removing that original DB clsuter in the primary region, from the global cluster, and then deleting the global cluster.


## 3. Build a new Global Database

In the **secondary region**, add a region (**Actions** --> **Add Region**) for the DB cluster you have promoted named `auroralab-mysql-secondary`. Select the original primary region to add to this new Global Database, utilizing the existing VPC, security group, parameter groups (instance and cluster), and role settings. Name the DB cluster `auroralab-mysql-restored` and name the DB instance `auroralab-mysql-node4`. Name the Global Database identifier as `auroralabs-mysql-temporary`

Allow 10-15 minutes for the new region replica in the previously primary region to be restored.

Once that process is complete, you will have a Global Database again, with a *primary DB cluster* in the **secondary region** and a *secondary cluster* in the **primary region**. You should wait until all nodes in your Global Database are indicated with a status of **Available** before proceeding.


## 4. Break the Global Database one more time

The objective is to *fail back*, which means restoring an equivalent to the original environment configuration. You need to promote the new secondary DB cluster in the **primary region**, named `auroralab-mysql-restored`, to be an independent DB cluster. Using the RDS Console in the **primary region**, select the cluster and choose **Actions** --> **Remove From Global**. This will promote it with the data intact and it will now become an independent DB cluster. 

## 5. Rebuild the final Global Database

In the **primary region**, add a region (**Actions** --> **Add Region**) for the DB cluster you have just promoted named `auroralab-mysql-restored`. Select the secondary region to add to this new Global Database, utilizing the existing VPC, security group, parameter groups (instance and cluster), and role settings. Name the DB cluster `auroralab-mysql-new-secondary` and name the DB instance `auroralab-mysql-node5`. Name the Global Database identifier as `auroralabs-mysql-global` (assuming you have deleted the old global cluster construct adter detaching the original primary cluster, if not name it something else).


## 6. Delete the old secondary DB cluster

In the secondary region, you can now delete the old secondary DB cluster, named `auroralab-mysql-secondary`. Now you should have an Aurora Global Database with one *primary DB cluster* in your **primary region** and a *secondary DB cluster* in the **secondary region**.


## 7. Summary

Now that you have the Global Database restored completely to its original regional configuration. Typically as you are promoting and extending the global database through the failback cycle, you will have to update the database endpoints your application is using to reflect all the intermediary steps, in order to avoid significant application downtime. As you have seen the endpoints may change several times, and the fail-back should be orchestrated gradually to ensure you have full DR capability at any given point in time.

In a real world scenario, you can combine this with Route53 friendly DNS names (CNAME records) to point to the different and changing Aurora reader and writer endpoints, to minimize the amount of manual work you have to undertake to re-link your applications due to failover and reconfiguration. You can read more about this in our <a href="https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-rds-db.html" target="_blank"> Route53 documentation</a>.
