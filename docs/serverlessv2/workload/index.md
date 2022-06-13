# Run workload and observe scaling

This lab will demonstrate how Aurora Serverless v2 performs <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-serverless-v2.how-it-works.html#aurora-serverless-v2.how-it-works.scaling" target="_blank">scaling</a> depending on the minimum and maximum ACU settings for the cluster. 

This lab contains the following tasks:

1. Generate load on your DB cluster
2. Create CloudWatch dashboard
3. Examine the scaling of your DB cluster

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/)
* [Connect to the Cloud9 Desktop](/prereqs/connect/)
* [Create a New DB Cluster](/serverlessv2/create/) (conditional, only if you plan to create a cluster manually)


## 1. Generate load on your DB cluster

We will use a python script to generate load on the Aurora Serverless v2 cluster. If you have not already opened a terminal window in the Cloud9 desktop in a previous lab, please [following these instructions](/prereqs/connect/) to do so now. Once connected, run the load generation script from the terminal window, replacing the [clusterEndpoint] placeholder with your Aurora Serverless v2 cluster endpoint. To identify the **Cluster Endpoint**, choose the tab below that best matches your circumstances, and run the indicated command:

=== "The DB cluster has been pre-created for me"
    If AWS CloudFormation has provisioned the DB cluster on your behalf, and you skipped the **Create an Aurora Serverless v2 DB Cluster** lab, please go to the <a href="https://console.aws.amazon.com/rds/" target="_blank">RDS Console</a> and use the name of the pre-created Serverless v2 cluster.


=== "I have created the DB cluster myself"
    If you have completed the [Create an Aurora Serverless v2 DB Cluster](/serverlessv2/create/) lab, and created the Aurora Serverless v2 DB cluster manually replace the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster.

```
python3 serverlessv2_demo.py -e[clusterEndpoint] -u$DBUSER -p$DBPASS -dmyshop
```

<!---??? tip "What do all these parameters mean?"
    Parameter | Description
    --- | ---
    --cluster endpoint | writer endpoint.
    --DBUSER | User.
    --DBPass | Additional command parameters.-->

The command will report the number of current connections, total threads started with the database and it will also show the Innodb Buffer Pool Size, InnoDB History List Length growing with the number of connections. 

<span class="image">![Cloud 9](python-script-run.png?raw=true)</span>

## 2. Create CloudWatch dashboard 

While the command is running, open the <a href="https://console.aws.amazon.com/cloudwatch/" target="_blank">Amazon CloudWatch console</a> in a different browser tab.

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

In the navigation pane, choose **Dashboards**, and then choose **Create dashboard**. In the Create new dashboard dialog box, enter name `aurora-serverless-v2` for the dashboard, and then choose **Create dashboard**. 

<span class="image">![Cloudwatch dashboard](cloudwatch-create-dash.png?raw=true)</span>

In the **Add Widget** dialog box, select **Line**. 

<span class="image">![Add Widget](line-widget.png?raw=true)</span>

Next, in the **Add to this dashboard** dialog box, choose **Metrics**.

<span class="image">![Add to this dashboard](select-metrics.png?raw=true)</span>

In the **Add metric graph** dialog box, choose **Source** and paste the following code (replace `auroralab-serverless-node-0` with the name of your writer instance). 

!!! note
    To find the name of your writer instance, go to the <a href="https://console.aws.amazon.com/rds/" target="_blank">RDS Console</a>, under **Databases** find the DB instance in the cluster that has the **Writer** role and click on the name, to view the DB instance details. 

<span class="image">![Writer Instance](writer-cpu-99.png?raw=true)</span>

After identifying the name of writer instance of your Aurora Serverless v2 cluster, replace it with `auroralab-serverless-node-0` in the below code and paste the code in **Source**

    {
        "metrics": [
            [ "AWS/RDS", "ServerlessDatabaseCapacity", "DBInstanceIdentifier", "auroralab-serverless-node-0", { "yAxis": "right" } ],
            [ "MyFlashSale/Orders", "Orders", "OfferType", "FlashSale", { "stat": "Sum" } ]
        ],
        "view": "timeSeries",
        "stacked": false,
        "region": "us-east-2",
        "stat": "Average",
        "period": 1,
        "yAxis": {
            "left": {
                "label": "Orders",
                "min": 0,
                "max": 100,
                "showUnits": false
            },
            "right": {
                "label": "ACU",
                "min": 0,
                "max": 10,
                "showUnits": false
            }
        }
    }

Click on **Update** and then choose **Create widget**. 

<span class="image">![Create Widget](create-widget.png?raw=true)</span>

Finally, select **Save dashboard** on the top right corner. 

<span class="image">![Save](save-dashboard.png?raw=true)</span>

## 3. Examine the scaling 

To expand the widget, hover on it and click on **Maximize** icon. You will be able to see a similar graph as shown below which is a plot of **Orders** vs **ACU - Aurora Capacity Unit**. The number of Orders (orange line) are graphed against the Aurora Serverless v2 database capacity (blue line). As can be seen in the graph, at the start of the workload, the Serverless v2 cluster is at the **Minimum ACUs** of 0.5, as the orders increased, the cluster scaled to the **Maximum ACUs** of 9 and as the orders decreased it would continue to scale down. 

<span class="image">![Scaling graph](final-scaling.png?raw=true)</span>

The metrics displayed by the dashboard are a moving time window. You can adjust the size of the time window by clicking the buttons across the top right of the interface (`1h`, `3h`, `12h`, `1d`, `Custom`). You can also zoom into a specific period of time by dragging across the graphs.

!!! note
    All dashboard views are time synchronized. Zooming in will adjust all views, including the detailed drill-down section at the bottom.

<!---Section | Filters | Description
--- | --- | ---
**ACU** Aurora capacity unit-->

You can now toggle back to the Cloud9 desktop terminal, and type `CTRL+C` to quit the load generator. After a while the Aurora Serverless v2 cluster would scale to the **Minimum ACUs** of 0.5 automatically. While you are welcome to wait until that happens, you may also proceed with the next lab at this point.



