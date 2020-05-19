# Use Query Plan Management (QPM)

This lab will demonstrate how to use the <a href="https://aws.amazon.com/blogs/database/introduction-to-aurora-postgresql-query-plan-management/" target="_blank">Query plan management (QPM)</a> feature of Aurora  PostgreSQL. It allows you to maintain stable, yet optimal, performance for a set of managed SQL statements.

Query plan management is available with Amazon Aurora PostgreSQL version 10.5-compatible (Aurora PostgreSQL 2.1.0) and later, or Amazon Aurora PostgreSQL version 9.6.11-compatible (Aurora PostgreSQL 1.4.0) and later. The quickest way to enable QPM is to use the automatic plan capture, which enables the plan capture for all SQL statements that run at least two times.

??? tip "Learn more about QPM"
    With query plan management, you can control execution plans for a set of statements that you want to manage. You can do the following:

    1. Improve plan stability by forcing the optimizer to choose from a small number of known, good plans.
    2. Optimize plans centrally and then distribute the best plans globally.
    3. Identify indexes that aren't used and assess the impact of creating or dropping an index.
    4. Automatically detect a new minimum-cost plan discovered by the optimizer.
    5. Try new optimizer features with less risk, because you can choose to approve only the plan changes that improve performance.

    For additional details on the Query Plan Management please refer official documentation <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Optimize.html" target="_blank"> Managing Query Execution Plans for Aurora PostgreSQL</a>.

This lab contains the following tasks:

1. Enable QPM and automatic plan capture in your DB cluster parameters
2. Connect to the DB cluster
3. Create and verify the apg_plan_mgmt extension for your DB instance
4. Run a synthetic workload with automatic capture
5. QPM plan adaptability with plan evolution mechanism
6. Fixing plans with QPM using pg_hint_plan
7. Deploying QPM-managed plans globally using export and import
8. Disabling QPM and deleting plans manually

This lab requires the following prerequisites:

* [Get Started](/win/)
* [Connect to your Aurora PostgreSQL DB cluster](/win/apg-connect/)


## 1. Enable QPM and automatic plan capture in your DB cluster parameters

Open the <a href="https://eu-west-1.console.aws.amazon.com/rds/home?region=eu-west-1" target="_blank">Amazon RDS service console</a>. In the navigation pane, choose **Parameter groups**.

<span class="image">![RDS Dashboard](rds-dashboard.png?raw=true)</span>

In the list, choose the parameter group for your Aurora PostgreSQL DB cluster. You will find the name of the DB cluster parameter group in the **Outputs** section of the CloudFormation stack (see previous lab modules) using the key ==[postgresClusterParamGroup]==. It is in the format `mod-XXXXXXXXXXXXXXXX-pgclusterparams-XXXXXXXXX`.

!!! note
    Aurora DB clusters use two parameter groups, one at the DB cluster level, with settings that apply cluster-wide, one at the DB instance level, with settings that apply to that specific instance only. Since the values in the default parameter groups cannot be changed, your cluster is using a custom DB cluster parameter group and a custom DB instance parameter group.

    Please make sure you select the parameter group of **Type** `DB cluster parameter group` at this step, you will change the instance level one after that.

<span class="image">![RDS Parameter Groups](rds-param-groups-list.png?raw=true)</span>

Click on the DB cluster parameter group selected above and then click on **Edit parameters**.

<span class="image">![RDS Parameter Group Details](rds-param-groups-detail.png?raw=true)</span>

Set the value of the **rds.enable_plan_management** parameter to `1` and click **Save changes**.

<span class="image">![RDS Parameter Group Changes](rds-param-groups-change.png?raw=true)</span>

Go back to the list of parameters, and select the DB instance parameter group. You will find the name of the DB cluster parameter group in the **Outputs** section of the CloudFormation stack (see previous lab modules) using the key ==[postgresNodeParamGroup]==. It is in the format `mod-XXXXXXXXXXXXXXXX-pgnodeparams-XXXXXXXXX`. Similarly, open your database level parameter group and click on **Edit parameters**.

<span class="image">![RDS Parameter Groups](rds-param-groups-list-node.png?raw=true)</span>

Using the same steps as above with the DB cluster parameter group, set the following parameters to the indicated values:

Name | Value
--- | ---
**apg_plan_mgmt.capture_plan_baselines** | `automatic`
**apg_plan_mgmt.use_plan_baselines** | `true`

!!! note
  Please note that these parameters can be set at either the cluster level or at the database level. The default recommendation would be to set it at the Aurora cluster level.

Click **Preview changes** to verify the changes, and then click **Save changes**.

<span class="image">![RDS Parameter Groups](rds-param-groups-preview.png?raw=true)</span>

You need to restart the DB instance for these changes to take effect. In the navigation pane, choose **Databases**.

In the `auroralab-postgres-cluster` DB cluster, choose the DB instance that is listed with the **Role** of `Writer`. Click on the **Actions** dropdown, and click **Reboot**.

<span class="image">![RDS Reboot DB Instance](rds-db-reboot.png?raw=true)</span>

Confirm by clicking **Reboot** at the prompt.

<span class="image">![RDS Reboot DB Instance](rds-db-reboot-confirm.png?raw=true)</span>

Wait for the **Status** of the DB instance to change to `Available` again. This will take several seconds, you may also refresh the listing or web page a few times to get a timely updates.


## 2. Connect to the DB cluster

Connect to the Aurora database just like you would to any other PostgreSQL-based database, using a compatible client tool. In this lab you will be using the `psql` command line tool to connect.

If you are not already connected to the Session Manager workstation command line, please connect [following these instructions](/win/apg-connect/). Once connected, find the DB cluster endpoint for your database in the **Outputs** of your CloudFormation stack under the key ==[postgresClusterEndpoint]==. If you have completed the connection instruction you have also retrieved the **username** and **password** for the database from Secrets Manager.

Run the following commands:

```shell
psql -h [postgresClusterEndpoint] -p 5432 -U masteruser -d mylab
```

You will be prompted for the password you have retrieved in the previous lab from the secret in AWS Secrets Manager.

To verify, you have connected successfully, run the following query:

```sql
SELECT aurora_version(), version();
```

You should see the following output if you have connected successfully:

```text
 aurora_version |                                   version                                   
----------------+-----------------------------------------------------------------------------
 2.3.5          | PostgreSQL 10.7 on x86_64-pc-linux-gnu, compiled by gcc (GCC) 4.9.3, 64-bit
(1 row)
```

## 3. Create and verify the apg_plan_mgmt extension for your DB instance.

Create the **apg_plan_mgmt** extension for your DB instance, using the following SQL commands, while still connected to the database:

```sql
CREATE EXTENSION apg_plan_mgmt;
```

Next, verify that the extension has been created:

```sql
SELECT extname, extversion FROM pg_extension WHERE extname = 'apg_plan_mgmt';
```

You should see the following result, if successful:

```text
    extname    | extversion
---------------+------------
 apg_plan_mgmt | 1.0.1
```

Validate that all QPM-related parameters are modified to the appropriate value.

Check if Query Plan Management is enabled:

```sql
SHOW rds.enable_plan_management;
```

Expected result:

```text
 rds.enable_plan_management
----------------------------
 1
```

Check if plan capture is automatic:

```sql
SHOW apg_plan_mgmt.capture_plan_baselines;
```

Expected result:

```text
 apg_plan_mgmt.capture_plan_baselines
--------------------------------------
 automatic
```

Check if plan usage is enabled:

```sql
SHOW apg_plan_mgmt.use_plan_baselines;
```

Expected result:

```text
 apg_plan_mgmt.use_plan_baselines
----------------------------------
 on
```

Disconnect from the database using the following command:

```sql
\q
```

## 4. Run a synthetic workload with automatic capture

The Cloud Formation template used for this workshop creates an EC2 bastion host bootstrapped with PostgreSQL tools (Pgbench, psql and sysbench etc.). The template will also initialize the database with pgbench (scale=100) data. You will use pgbench (a PostgreSQL benchmarking tool) to generate a simulated workload, which runs same queries for a specified period. With automatic capture enabled, QPM captures plans for each query that runs at least twice.

```shell
pgbench  --progress-timestamp -M prepared -n -T 100 -P 1  -c 500 -j 500  --host=[postgresClusterEndpoint] -b tpcb-like@1 -b select-only@20 --username=masteruser mylab
```

Re-connect to the database using the following command:

```shell
psql -h [postgresClusterEndpoint] -p 5432 -U masteruser -d mylab
```

You will be prompted for the password you have retrieved in the previous lab from the secret in AWS Secrets Manager.

Next, query the **apg_plan_mgmt.dba_plans** table to view the managed statements and the execution plans for the SQL statements issued with the pgbench tool.

```sql
SELECT sql_hash,
       plan_hash,
       status,
       enabled,
       sql_text
FROM   apg_plan_mgmt.dba_plans;
```

Results:

```text
  sql_hash   |  plan_hash  |   status   | enabled |                                               sql_text                                                
-1677381765	-225188843	 Approved   	 t       	UPDATE pgbench_branches SET bbalance = bbalance + $1 WHERE bid = $2;
-60114982	300482084	 Approved   	 t       	 INSERT INTO pgbench_history (tid, bid, aid, delta, mtime) VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP);
1319555216	30042398	 Approved   	 t       	select count(*) from pgbench_branches;

-2033469270	-1987991358	 Approved   	 t       	 UPDATE pgbench_tellers SET tbalance = tbalance + $1 WHERE tid = $2;
[......]
```

Capturing all plans with automatic capture has little runtime overhead and can be enabled in production.

Turn `off` automatic capture to make sure SQL statements outside the pgbench workload are not captured. Back in the RDS service console, follow the same steps as in section **1. Enable QPM and automatic plan capture in your DB cluster parameters** to set **apg_plan_mgmt.capture_plan_baselines** parameter to `off` in the DB instance-level parameter group.

<span class="image">![Turn off Automatic Plan Capture](rds-param-groups-change-off.png?raw=true)</span>

Verify that the parameter has been updated:

```sql
SHOW apg_plan_mgmt.capture_plan_baselines;
```

Expected result:

```text
 apg_plan_mgmt.capture_plan_baselines
--------------------------------------
 Off
```

Next, verify that the execution plan of the managed statement is the plan captured by QPM. Manually execute the explain plan on one of the managed statements from the result set above. The explain plan output show the SQL hash and the plan hash match with the QPM approved plan for that statement.

```sql
EXPLAIN (hashes true)  
UPDATE pgbench_tellers
SET    tbalance = tbalance + 100
WHERE  tid = 200;
```

Expected result:

```text
                         QUERY PLAN                                             
----------------------------------------------------------------------
 Update on pgbench_tellers  (cost=0.14..8.16 rows=1 width=358)
   ->  Index Scan using pgbench_tellers_pkey on pgbench_tellers  (cost=0.14..8.16 rows=1 width=358)
         Index Cond: (tid = 200)
 SQL Hash: -2033469270, Plan Hash: -1987991358
```

The **Plan Hash** is the same value when comparing the value in the list of captured plans, and the explain output: `-1987991358`.

In addition to automatic plan capture, QPM also offers manual capture, which offers a mechanism to capture execution plans for known problematic queries. Capturing the plans automatically is recommended generally. However, there are situations where capturing plans manually would be the best option, such as:

1. You don't want to enable plan management at the Database level, but you do want to control a few critical SQL statements only.
2. You want to save the plan for a specific set of literals or parameter values that are causing a performance problem.


## 5. QPM plan adaptability with plan evolution mechanism

If the optimizer's generated plan is not a stored plan, the optimizer captures and stores it as a new unapproved plan to preserve stability for the QPM-managed SQL statements.

Query plan management provides techniques and functions to add, maintain, and improve execution plans and thus provides Plan adaptability. Users can on demand or periodically instruct QPM to evolve all the stored plans to see if there is a better minimum cost plan available than any of the approved plans.

QPM provides the **apg_plan_mgmt.evolve_plan_baselines** function to compare plans based on their actual performance. Depending on the outcome of your performance experiments, you can change a plan's status from unapproved to either approved or rejected. You can instead decide to use the **apg_plan_mgmt.evolve_plan_baselines** function to temporarily disable a plan if it does not meet your requirements.

For additional details about the QPM Plan evolution, <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Optimize.Maintenance.html#AuroraPostgreSQL.Optimize.Maintenance.EvaluatingPerformance" target="_blank"> see Evaluating Plan Performance. </a>

For the first use case, we walk through an example on how QPM helps ensure plan stability, these changes can result in plan regression.

In most cases, you set up QPM to use automatic plan capture so that plans are captured for all statements that run two or more times. However, you can also capture plans for a specific set of statements that you specify manually.

To do this, you set **apg_plan_mgmt.capture_plan_baselines** to `off` by default. At the session level, you set **apg_plan_mgmt.capture_plan_baselines** to `manual`. You will see how to do this later in this lab.

Enable manual plan capture to instruct QPM to capture the execution plan of the desired SQL statements manually:

```sql
SET apg_plan_mgmt.capture_plan_baselines = manual;
```

Run an explain plan for the query so that QPM can capture the plan of the query (the following output for the explain plan is truncated for brevity):

```sql
EXPLAIN (hashes true)
SELECT Sum(delta),
       	    Sum(bbalance)
FROM   pgbench_history h,
       	   pgbench_branches b
WHERE  b.bid = h.bid
       AND b.bid IN ( 1, 2, 3 )
       AND mtime BETWEEN (SELECT Min(mtime)
                          FROM   pgbench_history mn) AND (SELECT Max(mtime)
                                                          FROM  pgbench_history mx);
```

Expected results:

```text
                      QUERY PLAN                                                  
----------------------------------------------------------------------
 Aggregate  (cost=23228.13..23228.14 rows=1 width=16)
   InitPlan 1 (returns $1)
     ->  Finalize Aggregate  (cost=6966.00..6966.01 rows=1 width=8)
           ->  Gather  (cost=6965.89..6966.00 rows=1 width=8)
                 Workers Planned: 1
                 ->  Partial Aggregate  (cost=5965.89..5965.90 rows=1 width=8)
                       ->  Parallel Seq Scan on pgbench_history mn  (cost=0.00..5346.11 rows=247911 width=8)
   InitPlan 2 (returns $3)
     ->  Finalize Aggregate  (cost=6966.00..6966.01 rows=1 width=8)
           ->  Gather  (cost=6965.89..6966.00 rows=1 width=8)
                 Workers Planned: 1
                 ->  Partial Aggregate  (cost=5965.89..5965.90 rows=1 width=8)
                       ->  Parallel Seq Scan on pgbench_history mx  (cost=0.00..5346.11 rows=247911 width=8)
   ->  Nested Loop  (cost=0.00..9292.95 rows=632 width=8)
         Join Filter: (h.bid = b.bid)
         ->  Seq Scan on pgbench_history h  (cost=0.00..9188.74 rows=2107 width=8)
               Filter: ((mtime >= $1) AND (mtime <= $3))
         ->  Materialize  (cost=0.00..14.15 rows=3 width=8)
               ->  Seq Scan on pgbench_branches b  (cost=0.00..14.14 rows=3 width=8)
                     Filter: (bid = ANY ('{1,2,3}'::integer[]))
[......]
SQL Hash: 1561242727, Plan Hash: -1990695905
```

Disable manual capture of the plan after you capture the execution plan for the desired SQL statement:

```sql
SET apg_plan_mgmt.capture_plan_baselines = off;
```

View the captured query plan for the query that ran previously. The plan_outline column in the table `apg_plan_mgmt.dba_plans` shows the entire plan for the SQL. For brevity, the plan_outline isn't shown here. Instead, **plan_hash_value** from the explain plan preceding is compared with **plan_hash** from the output of the `apg_plan_mgmt.dba_plans` query.

```sql
SELECT sql_hash,
       		 plan_hash,
       		status,
       		estimated_total_cost "cost",
       		sql_text
FROM apg_plan_mgmt.dba_plans;
```

Expected result:

```text
  sql_hash  		|  plan_hash  		|  status  	| cost 	|  sql_text                                                                                                         

------------+-------------+----------+---------+-----------------------------------------------------------
1561242727	-1990695905	 Approved 	 23228.14     	 select sum(delta),sum(bbalance) from pgbench_history h, pgbench_branches b where b.bid=h.bid and b.bid in (1,2,3) and mtime between (select min(mtime) from pgbench_history mn) and (select max(mtime) from pgbench_history mx);
```

To instruct the query optimizer to use the approved or preferred captured plans for your managed statements, set the parameter **apg_plan_mgmt.use_plan_baselines** to `true`:

```sql
SET apg_plan_mgmt.use_plan_baselines = true;
```

View the explain plan output to see that the QPM approved plan is used by the query optimizer:

```sql
EXPLAIN (hashes true)
SELECT Sum(delta),
       	    Sum(bbalance)
FROM   pgbench_history h,
       	   pgbench_branches b
WHERE  b.bid = h.bid
       AND b.bid IN ( 1, 2, 3 )
       AND mtime BETWEEN (SELECT Min(mtime)
                          FROM   pgbench_history mn) AND (SELECT Max(mtime)
                                                          FROM  pgbench_history mx);
```

Expected results:

```text
                      QUERY PLAN                                                  
----------------------------------------------------------------------
 Aggregate  (cost=23228.13..23228.14 rows=1 width=16)
   InitPlan 1 (returns $1)
     ->  Finalize Aggregate  (cost=6966.00..6966.01 rows=1 width=8)
           ->  Gather  (cost=6965.89..6966.00 rows=1 width=8)
                 Workers Planned: 1
                 ->  Partial Aggregate  (cost=5965.89..5965.90 rows=1 width=8)
                       ->  Parallel Seq Scan on pgbench_history mn  (cost=0.00..5346.11 rows=247911 width=8)
   InitPlan 2 (returns $3)
     ->  Finalize Aggregate  (cost=6966.00..6966.01 rows=1 width=8)
           ->  Gather  (cost=6965.89..6966.00 rows=1 width=8)
                 Workers Planned: 1
                 ->  Partial Aggregate  (cost=5965.89..5965.90 rows=1 width=8)
                       ->  Parallel Seq Scan on pgbench_history mx  (cost=0.00..5346.11 rows=247911 width=8)
   ->  Nested Loop  (cost=0.00..9292.95 rows=632 width=8)
         Join Filter: (h.bid = b.bid)
         ->  Seq Scan on pgbench_history h  (cost=0.00..9188.74 rows=2107 width=8)
               Filter: ((mtime >= $1) AND (mtime <= $3))
         ->  Materialize  (cost=0.00..14.15 rows=3 width=8)
               ->  Seq Scan on pgbench_branches b  (cost=0.00..14.14 rows=3 width=8)
                     Filter: (bid = ANY ('{1,2,3}'::integer[]))
[......]
SQL Hash: 1561242727, Plan Hash: -1990695905
```

Create a new index on the `pgbench_history` table column **mtime** to change the planner configuration and force the query optimizer to generate a new plan:

```sql
CREATE INDEX pgbench_hist_mtime ON pgbench_history(mtime);
```

View the explain plan output to see that QPM detects a new plan but still uses the approved plan and maintains the plan stability:

```sql
EXPLAIN (hashes true)
SELECT Sum(delta),
       	    Sum(bbalance)
FROM   pgbench_history h,
       	   pgbench_branches b
WHERE  b.bid = h.bid
       AND b.bid IN ( 1, 2, 3 )
       AND mtime BETWEEN (SELECT Min(mtime)
                          FROM   pgbench_history mn) AND (SELECT Max(mtime)
                                                          FROM  pgbench_history mx);
```

Expected results:

```text
                      QUERY PLAN                                                  
Aggregate  (cost=23228.13..23228.14 rows=1 width=16)
   InitPlan 1 (returns $1)
     ->  Finalize Aggregate  (cost=6966.00..6966.01 rows=1 width=8)
           ->  Gather  (cost=6965.89..6966.00 rows=1 width=8)
                 Workers Planned: 1
                 ->  Partial Aggregate  (cost=5965.89..5965.90 rows=1 width=8)
                       ->  Parallel Seq Scan on pgbench_history mn  (cost=0.00..5346.11 rows=247911 width=8)
   InitPlan 2 (returns $3)
     ->  Finalize Aggregate  (cost=6966.00..6966.01 rows=1 width=8)
           ->  Gather  (cost=6965.89..6966.00 rows=1 width=8)
                 Workers Planned: 1
                 ->  Partial Aggregate  (cost=5965.89..5965.90 rows=1 width=8)
                       ->  Parallel Seq Scan on pgbench_history mx  (cost=0.00..5346.11 rows=247911 width=8)
   ->  Nested Loop  (cost=0.00..9292.95 rows=632 width=8)
         Join Filter: (h.bid = b.bid)
         ->  Seq Scan on pgbench_history h  (cost=0.00..9188.74 rows=2107 width=8)
               Filter: ((mtime >= $1) AND (mtime <= $3))
         ->  Materialize  (cost=0.00..14.15 rows=3 width=8)
               ->  Seq Scan on pgbench_branches b  (cost=0.00..14.14 rows=3 width=8)
                     Filter: (bid = ANY ('{1,2,3}'::integer[]))
[......]
 Note: An Approved plan was used instead of the minimum cost plan.
 SQL Hash: 1561242727, Plan Hash: -1990695905, Minimum Cost Plan Hash: -794604077***
```

Please note the message at the end of the plan results: **Note: An Approved plan was used instead of the minimum cost plan.**

Run the following SQL query to view the new plan and status of the plan. To ensure plan stability, QPM stores all the newly generated plans for a managed query in QPM as unapproved plans.

The following output shows that there are two different execution plans stored for the same managed statement, as shown by the two different plan_hash values. Although the new execution plan has the minimum cost (lower than the approved plan), QPM continues to ignore the unapproved plans to maintain plan stability.   

The plan_outline column in the table `apg_plan_mgmt.dba_plans` shows the entire plan for the SQL. For the sake of brevity, the **plan_outline** is not shown here. Instead, **plan_hash_value** from the explain plan preceding is compared with **plan_hash** from the output of the `apg_plan_mgmt.dba_plans` query.

```sql
SELECT sql_hash,
       		 plan_hash,
       		status,
       		estimated_total_cost "cost",
       		sql_text
FROM apg_plan_mgmt.dba_plans;
```

Expected results:

```text
  sql_hash  		|  plan_hash  		|  status  	| cost 	|  sql_text                                                                                                         

------------+-------------+----------+---------+----------------------------
1561242727	-1990695905	 Approved 	 23228.14     	 select sum(delta),sum(bbalance) from pgbench_history h, pgbench_branches b where b.bid=h.bid and b.bid in (1,2,3) and mtime between (select min(mtime) from pgbench_history mn) and (select max(mtime) from pgbench_history mx);

1561242727	-794604077	 Unapproved 	 111.17     	 select sum(delta),sum(bbalance) from pgbench_history h, pgbench_branches b where b.bid=h.bid and b.bid in (1,2,3) and mtime between (select min(mtime) from pgbench_history mn) and (select max(mtime) from pgbench_history mx);
```

Next is an example of plan adaptability with QPM. This example evaluates the unapproved plan based on the minimum speedup factor. It approves any captured unapproved plan that is faster by at least 10 percent than the best approved plan for the statement. For additional details, <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Optimize.Maintenance.html#AuroraPostgreSQL.Optimize.Maintenance.EvaluatingPerformance" target="_blank"> see Evaluating Plan Performance in the Aurora documentation</a>.

```sql
SELECT apg_plan_mgmt.Evolve_plan_baselines (sql_hash, plan_hash, 1.1, 'approve')
FROM   apg_plan_mgmt.dba_plans
WHERE  status = 'Unapproved';
```

Expected results:

```text
NOTICE: [Unapproved] SQL Hash: 1561242727, Plan Hash: 1944377599, SELECT sum(delta),sum(bbalance) from pgbench_history h, pgbench_branches b where ...
NOTICE:      Baseline   [Planning time 0.693 ms, Execution time 316.644 ms]
NOTICE:      Baseline+1 [Planning time 0.695 ms, Execution time 213.919 ms]
NOTICE:      Total time benefit: 102.723 ms, Execution time benefit: 102.725 ms, Avg Log Cardinality Error: 3.53418, Cost = 111.16..111.17
NOTICE:      Unapproved -> Approved
```

After QPM evaluates the plan based on the speed factor, the plan status changes to approved. At this point, the optimizer can choose that plan for that managed statement now.

```sql
SELECT sql_hash,
       		 plan_hash,
       		status,
       		estimated_total_cost "cost",
       		sql_text
FROM apg_plan_mgmt.dba_plans;
```

Expected results:

```text
  sql_hash  		|  plan_hash  		|  status  	| cost 	|  sql_text                                                                                                         

------------+-------------+----------+---------+-----------------------------------------------------------
1561242727	-1990695905	 Approved 	 23228.14     	 select sum(delta),sum(bbalance) from pgbench_history h, pgbench_branches b where b.bid=h.bid and b.bid in (1,2,3) and mtime between (select min(mtime) from pgbench_history mn) and (select max(mtime) from pgbench_history mx);

1561242727	-794604077	 Approved 	 111.17     	 select sum(delta),sum(bbalance) from pgbench_history h, pgbench_branches b where b.bid=h.bid and b.bid in (1,2,3) and mtime between (select min(mtime) from pgbench_history mn) and (select max(mtime) from pgbench_history mx);
```

View the explain plan output to see whether the query is using the newly approved minimum cost plan:

```sql
EXPLAIN (hashes true)
SELECT Sum(delta),
       	    Sum(bbalance)
FROM   pgbench_history h,
       	   pgbench_branches b
WHERE  b.bid = h.bid
       AND b.bid IN ( 1, 2, 3 )
       AND mtime BETWEEN (SELECT Min(mtime)
                          FROM   pgbench_history mn) AND (SELECT Max(mtime)
                                                          FROM  pgbench_history mx);
```

Expected results:

```text
                                               QUERY PLAN                                                
-----------------------------------------------------------------------------
 Aggregate  (cost=111.16..111.17 rows=1 width=16)
   InitPlan 2 (returns $1)
     ->  Result  (cost=0.46..0.47 rows=1 width=8)
           InitPlan 1 (returns $0)
             ->  Limit  (cost=0.42..0.46 rows=1 width=8)
                   ->  Index Only Scan using pgbench_hist_mtime on pgbench_history mn  (cost=0.42..14882.41 rows=421449 width=8)
                         Index Cond: (mtime IS NOT NULL)
   InitPlan 4 (returns $3)
     ->  Result  (cost=0.46..0.47 rows=1 width=8)
           InitPlan 3 (returns $2)
             ->  Limit  (cost=0.42..0.46 rows=1 width=8)
                   ->  Index Only Scan Backward using pgbench_hist_mtime on pgbench_history mx  (cost=0.42..14882.41 rows=421449 width=8)
                         Index Cond: (mtime IS NOT NULL)
   ->  Hash Join  (cost=14.60..107.06 rows=632 width=8)
         Hash Cond: (h.bid = b.bid)
         ->  Index Scan using pgbench_hist_mtime on pgbench_history h  (cost=0.42..85.01 rows=2107 width=8)
               Index Cond: ((mtime >= $1) AND (mtime <= $3))
         ->  Hash  (cost=14.14..14.14 rows=3 width=8)
               ->  Seq Scan on pgbench_branches b  (cost=0.00..14.14 rows=3 width=8)
                     Filter: (bid = ANY ('{1,2,3}'::integer[]))
[......]
 SQL Hash: 1561242727, Plan Hash: -794604077
```

## 6. Fixing plans with QPM using pg_hint_plan

In some cases, the query optimizer doesn’t generate the best execution plan for the query. One approach to fixing this problem is to put query hints into your application code, but this approach is widely discouraged because it makes applications more brittle and harder to maintain, and in some cases, you can’t hint the SQL because it is generated by a 3rd party application. What we will show is how to use hints to control the query optimizer, but then to remove the hints and allow QPM to enforce the desired plan, without adding hints to the application code.

For this purpose, PostgreSQL users can use the **pg_hint_plan** extension to provide directives such as “scan method,” “join method,” “join order,”, or “row number correction,” to the optimizer.  The resulting plan will be saved by QPM, along with any GUC parameters you choose to override (such as **work_mem**).  QPM remembers any GUC parameter overrides and uses them when it needs to recreate the plan. To install and learn more about how to use the pg_hint_plan extension, see the pg_hint_plan documentation.

Working with pg_hint_plan is incredibly useful for cases where the query can’t be modified to add hints. In this example, use a sample query to generate the execution plan that you want by adding hints to the managed statement. Then associate this execution plan with the original unmodified statement.

Check if the plan capture is disabled:

```sql
SHOW apg_plan_mgmt.capture_plan_baselines;
```

Expected results:

```text
 apg_plan_mgmt.capture_plan_baselines
--------------------------------------
 off
(1 row)
```

Run the query with the hint to use. In the following example, use the “HashJoin” hint, which is a directive for the optimizer to choose the join method as HashJoin.

The original plan of the query without hints is as follows:

```sql
EXPLAIN (hashes true)
SELECT
   *
FROM
   pgbench_branches b
   JOIN
      pgbench_accounts a
      ON b.bid = a.bid
ORDER BY
   a.aid;                                                   
```

Expected results:

```text
                                QUERY PLAN                                                    
----------------------------------------------------------------------
 Nested Loop  (cost=0.42..181906.82 rows=1000000 width=465)
   Join Filter: (b.bid = a.bid)
   ->  Index Scan using pgbench_accounts_pkey on pgbench_accounts a  (cost=0.42..44165.43 rows=1000000 width=97)
   ->  Materialize  (cost=0.00..14.15 rows=10 width=364)
         ->  Seq Scan on pgbench_branches b  (cost=0.00..14.10 rows=10 width=364)
 SQL Hash: 356104612, Plan Hash: -451962956
```

Enable pg_hint_plan and manual plan capture:

```sql
SET pg_hint_plan.enable_hint = true;
SET apg_plan_mgmt.capture_plan_baselines = manual;
```

EXPLAIN the query with the hints you want to use. In the following example, use the HashJoin (a, b) hint, which is a directive for the optimizer to use a hash join algorithm to join from table a to table b:

The plan that you want with a hash join is as follows:

```sql
/*+ HashJoin(a b) */  EXPLAIN (hashes true)
SELECT
   *
FROM
   pgbench_branches b
   JOIN
      pgbench_accounts a
      ON b.bid = a.bid
ORDER BY
   a.aid;
```

Expected results:

```text
                            QUERY PLAN                                               
----------------------------------------------------------------------
 Gather Merge  (cost=240409.02..250138.04 rows=833334 width=465)
   Workers Planned: 2
   ->  Sort  (cost=239409.00..240450.67 rows=416667 width=465)
         Sort Key: a.aid
         ->  Hash Join  (cost=14.22..23920.19 rows=416667 width=465)
               Hash Cond: (a.bid = b.bid)
               ->  Parallel Seq Scan on pgbench_accounts a  (cost=0.00..22348.67 rows=416667 width=97)
               ->  Hash  (cost=14.10..14.10 rows=10 width=364)
                     ->  Seq Scan on pgbench_branches b  (cost=0.00..14.10 rows=10 width=364)
 SQL Hash: 356104612, Plan Hash: 1139293728
```

Verify that plan 1139293728 was captured. Note, your specific Plan Hash value may be a different value.

Next, view the captured plan and the status of the plan (replacing the plan hash value with the one you have derived).

```sql
SELECT sql_hash,
       plan_hash,
       status,
       enabled,
       sql_text
FROM   apg_plan_mgmt.dba_plans
WHERE plan_hash = 1139293728;
```

Expected results:

```text
  sql_hash  | plan_hash  |  status  | enabled |         sql_text          
-----------+------------+----------+---------+---------------------------
 356104612 | 1139293728 | Approved | t       | SELECT                   +
           |            |          |         |    *                     +
           |            |          |         | FROM                     +
           |            |          |         |    pgbench_branches b    +
           |            |          |         |    JOIN                  +
           |            |          |         |       pgbench_accounts a +
           |            |          |         |       ON b.bid = a.bid   +
           |            |          |         | ORDER BY                 +
           |            |          |         |    a.aid;

```

If necessary, approve the plan. In this case this is the first and only plan saved for statement 356104612 (your plan hash value may vary), so it was saved as an **Approved** plan. If this statement already had a baseline of approved plans, then this plan would have been saved as an **Unapproved** plan.

In general, to **Reject** all existing plans for a statement and then **Approve** one specific plan, you could call **apg_plan_mgmt.set_plan_status** twice, like this:

```sql
SELECT apg_plan_mgmt.set_plan_status (sql_hash, plan_hash, 'Rejected') from apg_plan_mgmt.dba_plans where sql_hash = 356104612;
SELECT apg_plan_mgmt.set_plan_status (356104612, 1139293728, 'Approved');
```

Remove the hint, turn off manual capture, turn on use_plan_baselines, and also verify that the desired plan is in use without the hint:

```sql
SET apg_plan_mgmt.capture_plan_baselines = off;
SET apg_plan_mgmt.use_plan_baselines = true;
EXPLAIN (hashes true)
SELECT
   *
FROM
   pgbench_branches b
   JOIN
      pgbench_accounts a
      ON b.bid = a.bid
ORDER BY
   a.aid;             
```

Expected results:

```text
                             QUERY PLAN                                               
----------------------------------------------------------------------
 Gather Merge  (cost=240409.02..337638.11 rows=833334 width=465)
   Workers Planned: 2
   ->  Sort  (cost=239409.00..240450.67 rows=416667 width=465)
         Sort Key: a.aid
         ->  Hash Join  (cost=14.22..23920.19 rows=416667 width=465)
               Hash Cond: (a.bid = b.bid)
               ->  Parallel Seq Scan on pgbench_accounts a  (cost=0.00..22348.67 rows=416667 width=97)
               ->  Hash  (cost=14.10..14.10 rows=10 width=364)
                     ->  Seq Scan on pgbench_branches b  (cost=0.00..14.10 rows=10 width=364)
 Note: An Approved plan was used instead of the minimum cost plan.
 SQL Hash: 356104612, Plan Hash: 1139293728, Minimum Cost Plan Hash: -451962956
```

## 7. Deploying QPM-managed plans globally using export and import (informational)

Large enterprise customers often have applications and databases deployed globally. They also often maintain several environments (Dev, QA, Staging, UAT, Preprod, and Prod) for each application database. However, managing the execution plans manually in each of the databases in specific AWS Regions and each of the database environments can be cumbersome and time-consuming.

QPM provides an option to export and import QPM-managed plans from one database to another database. With this option, you can manage the query execution centrally and deploy databases globally. This feature is useful for the scenarios where you investigate a set of plans on a preprod database, verify that they perform well, and then load them into a production database.

Here are the steps to migrate QPM-managed plans from one database to another. For additional details, <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraPostgreSQL.Optimize.Maintenance.html#AuroraPostgreSQL.Optimize.Maintenance.ExportingImporting" target="_blank"> see Exporting and Importing Plans</a>in the Aurora documentation.

1. Export the QPM-managed plan from the source system.
To do this, from the source database with the preferred execution plan, an authorized DB user can copy any subset of the apg_plan_mgmt.plans table to another table. That user can then save it using the pg_dump command. For additional details on the pg_dump, see pg_dump in the PostgreSQL documentation.  
2. Import the QPM-managed plan on the target system.
3. On the target system, copy any subset of the apg_plan_mgmt.plans table to another table, and then save it using the pg_dump command. This is an optional step to preserve any existing managed plans on the target system before importing new plans for the source system.
4. We have assumed that you have used pg_dump tar-format archive in step 1.  Use the pg_restore command to copy the .tar file into a new table (plan_copy). For additional details about the pg_restore, see pg_restore in the PostgreSQL documentation.  
5. Merge the new table with the apg_plan_mgmt.plans table.
6. Reload the managed plans into shared memory and remove the temporary plans table.

```sql
SELECT apg_plan_mgmt.reload(); -- Refresh shared memory with new plans.
DROP TABLE plans_copy; -- Drop the temporary plan table.
```

## 8. Disabling QPM and deleting plans manually

To disable the QPM feature, open your DB cluster parameter group and set the **rds.enable_plan_management** parameter to `0`.

Next, delete all the plans captured:

```sql
SELECT SUM(apg_plan_mgmt.delete_plan(sql_hash, plan_hash))
FROM apg_plan_mgmt.dba_plans;
```

Helpful SQL statements:

```sql
SELECT sql_hash,plan_hash,status,enabled,sql_text FROM apg_plan_mgmt.dba_plans;

SELECT sql_hash,plan_hash,status,estimated_total_cost "cost",sql_text FROM apg_plan_mgmt.dba_plans;
```
