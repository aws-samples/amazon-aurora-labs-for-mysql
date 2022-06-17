# Gather cluster details

In this section we will gather and note down the Cluster endpoint and the writer instance name. We will use this information in the next section of the lab.

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/)
* [Connect to the Cloud9 Desktop](/prereqs/connect/)
* [Create a new Aurora Serverless v2 DB Cluster](/serverlessv2/create/) (optional, only if you plan to create a cluster manually)

## 1. Locate the Aurora Cluster Endpoint

Open the <a href="https://console.aws.amazon.com/rds/home" target="_blank">Amazon RDS service console</a>, if you don't already have it open.


Click on **DB Instances**

<span class="image">![Cluster](1rdsconsole.png?raw=true)</span>


Click on the Aurora Serverless V2 Cluster Name.

<span class="image">![Cluster](2cluclick.png?raw=true)</span>


On the **Connectivity and Security** tab locate the **Endpoints** section and note down the endpoint that has Type **Writer instance**. This is your **cluster endpoint**, which you will need in the next section of the lab.

<span class="image">![Cluster](3clustername.png?raw=true)</span>



## 2. Locate the writer instance


Next, note down the instance name under the **DB identifier** column, that has the Role value as **Writer instance**. This is your **writer instance**, which you will need in the next section of the lab.

<span class="image">![Writer](4writerinstance.png?raw=true)</span>