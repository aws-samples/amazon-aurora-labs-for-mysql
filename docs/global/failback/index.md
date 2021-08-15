# Fail Back a Global Database

This is an optional lab. You will attempt to orchestrate the required operations to restore writable database access back in the primary region, after promoting the secondary DB cluster in the secondary region due to an unplanned failover. You will only see high level instructions. Please take your time in first planning out the reverse/restore actions, and feel free to raise your hand (if you are at an AWS event) to share with us your questions, thoughts and ideas!

This lab contains the following tasks:

1. Overview of failover and failback in Amazon Aurora
2. Build a new global database
3. Initiate a managed planned failover
4. Summary

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/) (choose the **Deploy Global DB** option)
* [Connect to the Cloud9 Desktop](/prereqs/connect/)
* [Deploy an Aurora Global Database](/global/deploy/)
* [Recover from an Unplanned Primary DB Cluster Failure](/global/failover/)


## 1. Overview of fail over and fail back in Amazon Aurora

As illustrated in the previous lab, an **unplanned failover** is the process of shifting application and database resources from the original primary region to a secondary disaster recovery region during a large scale infrastructure or service level interruption. 

You may be able to design an application that is completely stateless and could be launched in any region, however the relational database tier, with Aurora Global Database, has one single writer DB instance, and it requires promotion of the secondary DB cluster in order for it to begin serving write requests, when the primary region becomes unavailable. Changes are now only tracked on the DB cluster in the secondary region. This also required taking the secondary DB cluster out of the Aurora Global Database. The original Aurora Global Database remains, and replication continues with other secondary DB clusters in other regions if you have additional such extensions, and the primary region is healthy.

For DR testing and similar use cases, consider using a <a href="https://aws.amazon.com/blogs/database/managed-planned-failovers-with-amazon-aurora-global-database/" target="_blank">managed planned failover</a>, instead which maintains the topology of your global database.

When the large scale interruption is restored, you usually want to restore the environment to its original setting, and synchronizing the original primary region to become the master node to serve write traffic, back again. This process is called **failback**, an operation that would see us returning production to its original location after the disaster event and all normal operations restored, while keeping track and capturing all the changed data that has been written to the recently-promoted secondary region. As the original primary region's DB cluster may become available after a large scale interruption, you also want to avoid a *split-brain* scenario. 

To reiterate, for normal single-region scenarios, failover is automatic, and failback is usually unnecessary if the failover nodes are of the same instance family, type, and size. This also applies when the writer DB instance in the primary DB cluster of a global database fails. Failovers to other regions are typically not necessary in that case, as service is restored automatically in the same region. This type of planning is only needed in the extremely unlikely scenario of failing over / failing back to a different region, because of a complete and likely longer time workload disruption in the primary region.


## 2. Build a new global database

In the **secondary region**, add a region (**Actions** --> **Add AWS Region**) for the DB cluster you have promoted. Set the global database identifier to `auroralab-mysql-restored`. Select the original primary region to add to this new Global Database, utilizing the existing VPC, security group, parameter groups (instance and cluster), and role settings. Name the DB cluster `auroralab-mysql-new-primary` and name the DB instance `auroralab-mysql-node4`.

Allow 10-15 minutes for the new region replica in the previously primary region to be restored.

Once that process is complete, you will have a Global Database again, with a *primary DB cluster* in the **secondary region** and a *secondary cluster* in the **primary region**. You should wait until all nodes in your Global Database are indicated with a status of **Available** before proceeding.


## 3. Initiate a managed planned failover

Since the global database is now healthy, you can use the managed planned failover feature to move the primary region back to the original region. Select the newly created global database in the RDS service console, click the **Actions** button, and select **Fail over global database**. Next, choose the original region as the target in the **Choose a secondary cluster to become primary cluster** dropdown and click the **Fail over global database** button.


## 4. Summary

Now you have the global database restored to its original regional configuration. Typically as you are promoting and extending the global database through the failback cycle, you will have to update the database endpoints your application is using to reflect all the intermediary steps, in order to avoid significant application downtime. As you have seen the endpoints may change several times, and the fail-back should be orchestrated gradually to ensure you have full DR capability at any given point in time.

In a real world scenario, you can combine this with Route53 friendly DNS names (CNAME records) to point to the different and changing Aurora reader and writer endpoints, to minimize the amount of manual work you have to undertake to re-link your applications due to failover and reconfiguration. You can read more about this in our <a href="https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-rds-db.html" target="_blank"> Route53 documentation</a>.
