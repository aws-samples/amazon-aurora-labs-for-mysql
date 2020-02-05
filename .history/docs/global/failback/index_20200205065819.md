# Failback to Original Primary Region (Optional)

As we have just done in the previous module, we can see that **Failover** is the process of shifting application and database resources from its original primary region to a secondary disaster recovery region during a large scale infrastructure or service level interruption. 

You may be able to design an application that is completely stateless and could be launched in any region, however the relational database tier, with Aurora Global Database, remains having one single Writer, and we have seen that it required promotion of the secondary DB cluster in order for it to begin serving write requests. Changes are now only tracked on the DB cluster in the secondary Region. Note that this also required breaking the Aurora Global Database.

When the large scale interruption is restored, we usually want to restore the environment to its original setting, and synchronizing the original Primary Region to become the master node to serve write traffic. This process is called **Failback**, an operation that would see us returning production to its original location after the disaster event and all normal operations restored, while keeping track and capturing all the changed data that has been written to the recently-promoted Secondary Region. As the original primary region's DB cluster is now restored, we also want to avoid what we consider a *split-brain* syndrome. 

* To reiterate, for normal single-region scenarios, failover is automatic, and failback is usually unnecessary if the failover nodes are of the same instance family, type, and size. Remember that Amazon Aurora regional DB Clusters are available in AWS regions are in and of itself resilient with *over 3 Availability Zones*. This type of planning is only needed in the extremely unlikely scenario of failing over / failing back to a different region.

This is an *EXTRA CHALLENGE* module. You will only see high level instructions. Please take your time in first planning out the reverse/restore actions, and feel free to raise your hand (if you are at an AWS event) to share with us your thoughts and ideas!

## Restore Network Connections and End the Simulated Failure

>  **`Region 1 (Primary)`**

* We were previously simulating a large scale regional/service level interruption by associating a **Network ACL (NACL)** rule that denies all network traffic. Let's revert this to end the traffic block. Go to your **VPC** Console and assign the private subnets to associate the original default NACLs.

* Due to the data being stale and being outdated compared to the Secondary Region Aurora DB Cluster, the previous Aurora DB Cluster and DB Instance in the Primary Region are no longer needed. Using the RDS console, let's delete them (both DB Cluster and DB Instance in primary region **gdb1-cluster** and **gdb1-node1**) and take a final snapshot of the database before it is terminated. If it still remains, we will delete the empty Global DB identifier, named as **reinvent-dat348-gdb**

| Region | DB Cluster Name | Global/Regional | DB Cluster Status | Node Status |
| ------- | ------ | ------ | ------ | ----- |
| Region 1 | gdb1-cluster | Regional | Deleted | Deleted |
| Region 2 | gdb2-cluster | Regional | Available | Writer |

## Rebuild a new Global Database - Restore Data to Primary Region

>  **`Region 2 (Secondary)`**

* We will now Add Region for the DB Cluster in the previously secondary region **gdb2-cluster**. We will add the original primary region into this new Global Database, utilizing the existing VPC, Security Group, Parameter Groups (instance and cluster), and Role settings. We will name the DB Instance **gdb1-node2-restored** and name the DB Cluster **gdb1-cluster-restored**. We will name the Global Database identifier as **reinvent-dat348-gdb-restoring**

* Allow 10-15 minutes for the new region replica in the previously primary region to be restored.

* Once that process is complete, you will have a Global Database again, with **Master** node in Secondary Region and the **Reader** in Primary Region. You should wait until all nodes in your Global Database are indicated with a status of **Available** before proceeding

| Region | DB Cluster Name | Global/Regional | DB Cluster Status | Node Status |
| ------- | ------ | ------ | ------ | ----- |
| Region 1 | gdb1-cluster-restored | Global | Available | Reader |
| Region 2 | gdb2-cluster          | Global | Available | Writer |

## Breaking Global Database one more time

>  **`Region 1 (Primary)`**

* Remember that we are looking to *failback*, which would see us restore the original environment configuration. We will be doing another promotion of the Original Primary Region DB Cluster. (which is currently under *Reader* mode). Using the RDS Console, we will issue a command to Remove From Global for **gdb1-cluster-restored**. This will promote it with the data intact and it will now become a regional *Writer*. 

| Region | DB Cluster Name | Global/Regional | DB Cluster Status | Node Status |
| ------- | ------ | ------ | ------ | ----- |
| Region 1 | gdb1-cluster-restored | Regional | Available | Writer |
| Region 2 | gdb2-cluster          | Regional | Available | Writer |

## Delete Secondary Region DB Cluster

>  **`Region 2 (Secondary)`**

* As both **gdb1-cluster-restored** and **gdb2-cluster** are now their own regional DB Clusters in their own respective regions, and we want to utilize the Primary Region as the master *Writer* in order to restore the original configuration.  Using the RDS console, let's delete them (both DB Cluster and DB Instance in Secondary Region  **gdb2-cluster** and **gdb2-node1**) and take a final snapshot of the database before it is terminated. If it still remains, we will delete the empty Global DB identifier, named as **reinvent-dat348-gdb-restoring**

| Region | DB Cluster Name | Global/Regional | DB Cluster Status | Node Status |
| ------- | ------ | ------ | ------ | ----- |
| Region 1 | gdb1-cluster-restored | Regional | Available | Writer |
| Region 2 | gdb2-cluster          | Regional | Deleted | Deleted |

## Rebuild the final Global Database - Restore Data to Secondary Region

>  **`Region 1 (Primary)`**

* We will now Add Region for the DB Cluster in the primary region **gdb1-cluster-restored**. We will add the secondary region back into the Global Database, utilizing the existing VPC, Security Group, Parameter Groups (instance and cluster), and Role settings. We will name the DB Instance **gdb2-node2-restored** and name the DB Cluster **gdb2-cluster-restored**. We will name the Global Database identifier as **reinvent-dat348-gdb-restored**.

| Region | DB Cluster Name | Global/Regional | DB Cluster Status | Node Status |
| ------- | ------ | ------ | ------ | ----- |
| Region 1 | gdb1-cluster-restored | Global | Available | Writer |
| Region 2 | gdb2-cluster-restored | Global | Available | Reader |

## Gather New Aurora Reader and Writer Endpoints

>  **`Region 1 (Primary)`** and >  **`Region 2 (Secondary)`**

* Now that we have the Global Database restored completely to its original regional configuration, we will grab the new endpoints for both the Primary Region writer and Secondary Region reader. The endpoint addresses have all been changed because we have deleted the previous DB Cluster pair for a new pair in our process to failback.

* Return to each instance of Apache Superset using both the **Apache Superset Primary URL** and **Apache Superset Secondary URL**. Perform the following:
  * In Primary Superset instance, edit your ``mysql aurora-gdb1-write`` data source, and update the endpoint to reflect the new Primary Region DB Cluster Writer Endpoint.
  * In Secondary Superset instance, edit your ``mysql aurora-gdb2-read`` data source, and update the endpoint to reflect the new Secondary Region DB Cluster Reader Endpoint.
  * If you recall, we added ``mysql aurora-gdb2-write`` data source, you can remove this one as the Secondary Region DB Cluster Writer Endpoint is not activated.
    * Or, you can opt to modify this to connect cross-region back to the master Primary Region Writer Endpoint, simply edit this data source name to ``mysql aurora-gdb1-write``, and update the endpoint to reflect the new Primary Region DB Cluster Writer Endpoint.
 
* In a real world scenario, you can combine this with Route53 friendly DNS names (CNAME records) to point to the different and changing Aurora reader and writer endpoints, to minimize the amount of manual work you have to undertake to re-link your applications due to failover and reconfiguration. You can read more about this in our <a href="https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/routing-to-rds-db.html" target="_blank"> documentation</a>.

## Summary

![Failback Architecture (Midway)](failback-arch1.png)

The architecture diagram above shows the *midpoint* of your failback operation, as you have restored your Aurora Global Database, with the secondary region acting as the *Writer*.

* **Congratulations!** You have now completed the extra Failback challenge. You have a better understanding that failover and failback cross-region, can be a potentially intrusive operation that is best handled with proper planning in order to minimize split-brain scenario. Test your disaster recovery plans often and update your runbooks accordingly - include failover and failback in these tests.