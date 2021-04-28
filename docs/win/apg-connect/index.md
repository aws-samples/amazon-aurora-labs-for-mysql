# Connect to your Aurora PostgreSQL DB cluster

To interact with the Aurora database cluster, you will use an <a href="https://aws.amazon.com/ec2/" target="_blank">Amazon EC2</a> Linux instance that acts like a workstation to interact with the AWS resources in the labs on this website. All necessary software packages and scripts have been installed and configured on this EC2 instance for you. To ensure a unified experience, you will be interacting with this workstation using <a href="https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html" target="_blank">AWS Systems Manager Session Manager</a>. With Session Manager you can interact with your workstation directly from the management console, without the need to install any software on your own devices.

!!! note
    At this time, you have completed the Aurora MySQL portion of this workshop. you may close the command line windows and tabs used for those labs, if you like, and to eliminate any confusion. The following Aurora PostgreSQL labs use a different set of resources, in order to provide a consistent experience.

This lab contains the following tasks:

1. Get the parameters from the Team Dashboard
2. Retrieve database credentials from AWS Secret Manager
3. Connecting to the EC2 bastion instance with Systems Manager
4. Connect to the DB cluster

This lab requires the following prerequisites:

* [Get Started](/win/)


## 1. Get the parameters from the Team Dashboard

At the end of the getting started step, you have reviewed the parameters for your lab environment. For the following Aurora PostgreSQL labs, you will need the following values for lab resources:

Resource name | Value
--- | ---
Cluster Parameter Group | Refer to: ==[postgresClusterParamGroup]== on the Team Dashboard
Database Parameter Group | Refer to: ==[postgresNodeParamsGroup]== on the Team Dashboard
Cluster Endpoint | Refer to: ==[postgresClusterEndpoint]== on the Team Dashboard
Reader Endpoint	| Refer to: ==[postgresReaderEndpoint]== on the Team Dashboard
Secret Name	| Refer to: ==[secretArn]== on the Team Dashboard
DB name	| `mylab`
DB username	| `masteruser`
DB password	| See below for steps how to retrieve

## 2. Retrieve database credentials from AWS Secrets Manager

Open the <a href="https://eu-west-1.console.aws.amazon.com/secretsmanager/home?region=eu-west-1#/listSecrets" target="_blank">AWS Secrets Manager service console</a>, and search for the secret name shown in the output of the stack (normally there is only one secret listed in the correct region). Click on the name of that secret.

<span class="image">![Listing of Secrets](secret-list.png?raw=true)</span>

On the secret's detail page, click on the **Retrieve secret value** button. Note down the **username** and **password**, you will need them in later labs.

<span class="image">![Secret Details](secret-details.png?raw=true)</span>

<span class="image">![Secret Credentials](secret-credentials.png?raw=true)</span>

## 3. Connect to the EC2 workstation using AWS Systems Manager

Open the <a href="https://eu-west-1.console.aws.amazon.com/systems-manager/session-manager?region=eu-west-1" target="_blank">Systems Manager: Session Manager service console</a> and click **Start session**.

<span class="image">![SSM Listing](ssm-listing.png?raw=true)</span><br>

Select the instance named `auroralab-postgres-bastion`, then click **Start session**.

<span class="image">![SSM Select Instance](ssm-select.png?raw=true)</span><br>

By default Session Manager connects using the login **ssm-user**. You need to switch to **ec2-user** using the following command:

```shell
sudo su -l ec2-user
```

You can verify that you are using the correct **ec2-user** account by using the following command:

```shell
whoami
```

<span class="image">![SSM Terminal](ssm-terminal.png?raw=true)</span><br>

Next, update the `$PATH` environment variable with the location of the PostgreSQL client tools:

```shell
export PATH=/home/ec2-user/postgresql-10.7/src/bin/:/home/ec2-user/postgresql-10.7/src/bin/pgbench:$PATH
```

## 4. Connect to the DB cluster

Connect to the Aurora database just like you would to any other PostgreSQL database, using a compatible client tool. In this lab you will be using the `psql` command line tool to connect.

Run the command below, replacing the ==[postgresClusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. You will find the value for the cluster endpoint parameter on the Team Dashboard web page.

```shell
psql -h [postgresClusterEndpoint] -p 5432 -U masteruser -d mylab
```

Once connected you can issue SQL commands to the database. List the available databases using:

```sql
\l
```

You should see a result similar to the example below:

```text
                                     List of databases
   Name    |   Owner    | Encoding |   Collate   |    Ctype    |     Access privileges
-----------+------------+----------+-------------+-------------+---------------------------
 mylab     | masteruser | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
 postgres  | masteruser | UTF8     | en_US.UTF-8 | en_US.UTF-8 |
 rdsadmin  | rdsadmin   | UTF8     | en_US.UTF-8 | en_US.UTF-8 | rdsadmin=CTc/rdsadmin
 template0 | rdsadmin   | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/rdsadmin              +
           |            |          |             |             | rdsadmin=CTc/rdsadmin
 template1 | masteruser | UTF8     | en_US.UTF-8 | en_US.UTF-8 | =c/masteruser            +
           |            |          |             |             | masteruser=CTc/masteruser
(5 rows)
```

Quit out of the database client using the following command:

```sql
\q
```
