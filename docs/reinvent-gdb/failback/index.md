# Failback to Original Primary Region (Optional)

As we have just done in the previous module, we can see that **Failover** is the process of shifting application and database resources from its original primary region to a secondary disaster recovery region during a large scale infrastructure or service level interruption. 

You may be able to design an application that is completely stateless and could be launched in any region, however the relational database tier, with Aurora Global Database, remains having one single Writer, and we have seen that it required promotion of the secondary DB cluster in order for it to begin serving write requests. Changes are now only tracked on the DB cluster in the secondary Region. Note that this also required breaking the Aurora Global Database.

When the large scale interruption is restored, we usually want to restore the environment to its original setting, and synchronizing the original Primary Region to become the master node to serve write traffic. This process is called **Failback**, an operation that would see us returning production to its original location after the disaster event, while keeping track and capturing all the changed data that has been written to the recently promoted Secondary Region. As the original primary region's DB cluster is now restored, we also want to avoid what we consider a *split-brain* syndrome. 

This is an *EXTRA CHALLENGE* module. You will only see high level instructions. Please take your time in first planning out the reverse/restore actions, and feel free to raise your hand (if you are at an AWS event) to share with us your thoughts and ideas!

## Restore Network Connections and End the Simulated Failure

>  **`Region 1 (Primary)`**

* We were previously simulating a large scale regional/service level interruption by using a **Network ACL** that denies all network traffic. Go to your **VPC** Console and assign the subnets to use the original default NACLs.

* As the previous Aurora DB cluster and instance in the Primary Region is no longer needed. Using the RDS console, let's delete them (both cluster and instance in primary region) and take a final snapshot of the database before it is terminated. If it still remains, we will delete the empty Global DB identifier, named as **reinvent-dat348-gdb**

## Rebuild a new Global Database

>  **`Region 2 (Secondary)`**

* We will now Add Region for the DB cluster in the previously secondary region. We will add the original primary region into the Global Database, utilizing the existing VPC, Security Group, Parameter Groups (instance and cluster), and Role settings. We will name the instance **gdb1-restored-node** and name the cluster **gdb1-cluster**. We will name the Global Database identifier as **reinvent-dat348-gdb**

* Allow 10-15 minutes for the new region replica in the previously primary region to be restored.

* Once that process is complete, you will have a Global Database again, with **Master** node in Secondary Region and the **Reader** in Primary Region.




