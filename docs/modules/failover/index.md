# Testing Fault Tolerance

This lab will test the high availability and fault tolerance features provided by Amazon Aurora. You can find more details on the <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Concepts.AuroraHighAvailability.html" target="_blank">high availability</a> features and <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.Endpoints.html" target="_blank">connection management</a> best practices in our documentation. These tests are designed to touch upon the most important aspects of failure recovery, and are not intended to be exhaustive for all failure conditions.

This lab contains the following tasks:

1. Understanding fault tolerance
2. Test preparation
3. Testing a manual DB cluster failover
4. Testing fault injection queries

This lab requires the following lab modules to be completed first:

* [Prerequisites](/modules/prerequisites/)
* [Creating a New Aurora Cluster](/modules/create/) (conditional, if creating a cluster manually)
* [Connecting, Loading Data and Auto Scaling](/modules/connect/) (connectivity section only)
* [Using Performance Insights](/modules/perf-insights/) (generating load section only)


## 1. Understanding fault tolerance

In Amazon Aurora, high availability (HA) is implemented by deploying a cluster with a minimum of two DB instances, a writer in one Availability Zone, and a reader in a different Availability Zone. We call this configuration **Multi-AZ**. If you have provisioned the DB cluster using CloudFormation in the [Prerequisites](/modules/prerequisites/) lab, or have created the DB cluster manually, by following the [Creating a New Aurora Cluster](/modules/create) lab, you have deployed a **Multi-AZ** Aurora DB cluster.

In the event of a failure, Amazon Aurora will either restart the database engine within the same DB instance, or promote one of the reader DB instances as the new writer, depending on the circumstances, to restore operations as quickly as possible. It is therefore recommended to use the <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.Overview.Endpoints.html#Aurora.Overview.Endpoints.Types" target="_blank">relevant DB cluster endpoints</a> to connect to Amazon Aurora, as the role of 'writer' can shift from one DB instance to another in the event of a fault, and the cluster endpoints are always updated to reflect such changes.

Your client application should not cache the resolved DNS response for these endpoints beyond the specified time-to-live (TTL) - usually 1 second, should attempt to reconnect if disconnected, and should always verify whether the connected DB instance has the intended role (writer or reader).

## 2. Test preparation

In this lab we will use this [monitoring script](/scripts/dns-failover.py) to check the status of the database. The script is designed to test the fault tolerance of the writer DB instance. It will attempt to connect to the DB cluster's **Cluster Endpoint**, and check the status of the DB instance by executing the following SQL query:

```
SELECT @@innodb_read_only, @@aurora_server_id, @@aurora_version;
```

Variable | Expected Value | Description
--- | --- | ---
innodb_read_only | `0` for writers, `1` for readers | This global system variable indicates whether the storage engine was opened in read-only mode or not.
aurora_server_id | `labstack-[...]` | This is the value of the DB instance identifier configured for that particular cluster member at creation time
aurora_version | e.g. `1.19.5` | This is the version of the Amazon Aurora MySQL database engine running on your DB cluster. Note, these version numbers are different than the MySQL version.

In the event of a fault, the script will report the number of seconds it takes to reconnect to the intended endpoint and the writer role.

You will need to open two command line sessions to your EC2-based workstation. We will execute commands in one, and see the results in the other session. [See the Connecting, Loading Data and Auto Scaling lab](/modules/connect/#1-connecting-to-your-workstation-ec2-instance), for steps how to create a Session Manager command line session. It will also be more effective if the two browser windows are side by side.


## 3. Testing a manual DB cluster failover

In one of the two command line sessions, start the monitoring script using the following command:

```
python3 dns-failover.py -e [clusterEndpoint] -u $DBUSER -p "$DBPASS"
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
--- | --- | --- | --- | ---
-e | [clusterEndpoint] | See CloudFormation stack output | See previous lab | The cluster endpoint of the Aurora DB cluster.
-u | `$DBUSER` | Set automatically, see Secrets Manager | `masteruser` or manually set | The user name of the MySQL user to authenticate as.
-p | `$DBPASS` | Set automatically, see Secrets Manager | Manually set | The password of the MySQL user to authenticate as.

You can quit the monitoring script at any time by pressing `Ctrl+C`.

!!! warning "Cluster Endpoint"
    Please ensure you use the **Cluster Endpoint** and not a different endpoint for the purposes of this test. If you encounter an error, starting the script, please verify that the endpoint is correct.

<span class="image">![Initialize Sessions](2-initialize-sessions.png?raw=true)</span>

In the other command line session, you will trigger a manual failover of the cluster. During this process, Amazon Aurora will promote the reader as the new writer DB instance and demote the old writer to a reader role. The process will take several seconds to complete and will disconnect the monitoring script as well as other database connections. All DB instances in the cluster will be restarted.

Enter the following command in the command line session that does not run the monitoring script:

```
aws rds failover-db-cluster \
--db-cluster-identifier labstack-cluster
```

Wait and observe the monitor script output. It can take some time for Amazon Aurora to initiate the failover. Once the failover occurs, you should see monitoring output similar to the example below.

<span class="image">![Trigger DNS Failover](3-dns-failover.png?raw=true)</span>

**Observations:**

* Initially, the Cluster DNS endpoint resolves to the IP address of one of the cluster DB instances (`labstack-node-01` in the example above). The monitoring script connects to that particular DB instance and determines it is a writer.
* When the actual failover is implemented by the AWS automation, the monitoring script stops being able to connect to the database engine, as both the writer and the reader DB engines are being rebooted and re-configured.
* After several seconds, the monitoring script is able to connect again to the DB engine, but DNS has not fully updated yet, so it still connects to the old writer DB instance, which is now a reader. This underscores the importance of verifying the role of the engine upon establishing connections or borrowing them from a connection pool. The monitoring script correctly detects the discrepancy, and continues attempting to re-connect to the correct endpoint.
* After several additional seconds, the monitoring script is able to connect to the correct new writer DB instance (`labstack-node-02` in the example above), after the cluster endpoint has been re-configured automatically to point to the new writer, and DNS TTL has expired client-side. In the example above, the total client side observed failover disruption was ~15 seconds.
* In the event of a true hardware failure, you will likely not be able to connect to the old writer instance. But the client may attempt to connect until the attempt times out. A very long `connect_timeout` value in the client MySQL driver configuration may delay recovery for a longer period of time. However, there are other use cases where you would want to initiate a manual failover, such as scaling the compute of writer DB instances with minimal disruption.
* Because of the nature of DNS resolution and caching, you may also experience a *flip-flop* effect as clients might cycle between the reader and writer for a short span of time following the failover.

Feel free to repeat the failover procedure a few times to determine if there are any significant variances.


## 4. Testing fault injection queries

<a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/AuroraMySQL.Managing.FaultInjectionQueries.html" target="_blank">Fault injection queries</a> provide a mechanism to simulate a variety of faults in the operation of the DB cluster. They are used to test the tolerance of client applications to such faults. They can be used to:

* Simulate crashes of the critical services running on the DB instance. These do not typically result in a failover to a reader, but will result in a restart of the relevant services.
* Simulate disk subsystem degradation or congestion, whether transient in nature or more persistent.
* Simulate read replica failures

In this test we will simulate a crash of the database engine service on the DB instance. This type of crash can be encountered in real circumstances as a result of out-of-memory conditions, or other unexpected circumstances.

Connect to the cluster endpoint using a MySQL client in the command line session that does not run the monitoring script:

```
mysql -h [clusterEndpoint] -u$DBUSER -p"$DBPASS" mylab
```

**Command parameter values at a glance:**

Parameter | Parameter Placeholder | Value<br/>DB cluster provisioned by CloudFormation | Value<br/>DB cluster configured manually | Description
--- | --- | --- | --- | ---
-h | [cluster endpoint of clone] | See above | See above | The cluster endpoint of the Aurora cloned DB cluster.
-u | `$DBUSER` | Set automatically, see Secrets Manager | `masteruser` or manually set | The user name of the MySQL user to authenticate as.
-p | `$DBPASS` | Set automatically, see Secrets Manager | Manually set | The password of the MySQL user to authenticate as.
| [database] | `mylab` | `mylab` or manually set | The schema (database) to use by default.

Now, issue the following fault injection command:

```
ALTER SYSTEM CRASH INSTANCE;
```

Wait and observe the monitor script output. Once triggered, you should see monitoring output similar to the example below.

<span class="image">![Trigger Fault Injection](4-fault-injection.png?raw=true)</span>

**Observations:**

* When the crash is triggered, the monitoring script stops being able to connect to the database engine.
* After a few seconds the monitoring script is able to connect again to the DB engine.
* The role of the DB instance has not changed, the writer is still the same DB instance (`labstack-node-01` in the example above).
* There is no DB instance reconfiguration needed, and no DNS changes are needed either. As a result the recovery is significantly faster. In the example above, the total client side observed failover disruption was ~3 seconds.
