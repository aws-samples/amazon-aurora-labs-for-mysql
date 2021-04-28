<<<<<<< HEAD
# Machine Learning on Amazon Aurora 

Machine Learning integration with Amazon aurora currently supports Comprehend and Sagemaker. We will follow steps in this lab to create and run functions that will seamlessly and securely call Comprehend and Sagemaker in the background.

## Pre-requisites
Before running the lab make sure you have met the following pre-requisites.

* [Deploy Environment](/prereqs/environment/)
* [Connect to the Session Manager Workstation](/prereqs/connect/)

Once you have an Amazon Aurora clustered provisioned and established a session to the bastion host, execute the commands below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. This will connect you to the Aurora mysql  instance.

``` shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS"
```

Once connected, execute the following SQL queries to create the mltest database and tables and populate it with data. We will use these tables later in the lab for sentiment analysis and Sagemaker based predictions.

```sql
CREATE DATABASE mltest;
USE mltest;

CREATE TABLE IF NOT EXISTS comments (
comment_id INT AUTO_INCREMENT PRIMARY KEY,
comment_text VARCHAR(255) NOT NULL
);

INSERT INTO comments (comment_text)
VALUES ("This is very useful, thank you for writing it!");
INSERT INTO comments (comment_text)
VALUES ("Awesome, I was waiting for this feature.");
INSERT INTO comments (comment_text)
VALUES ("An interesting write up, please add more details.");
INSERT INTO comments (comment_text)
VALUES ("I don’t like how this was implemented.");
INSERT INTO comments (comment_text)
VALUES ("Horrible writing, I have read better books.");

CREATE TABLE `churn` (
`state` varchar(2048) DEFAULT NULL,
`acc_length` bigint(20) DEFAULT NULL,
`area_code` bigint(20) DEFAULT NULL,
`int_plan` varchar(2048) DEFAULT NULL,
`vmail_plan` varchar(2048) DEFAULT NULL,
`vmail_msg` bigint(20) DEFAULT NULL,
`day_mins` double DEFAULT NULL,
`day_calls` bigint(20) DEFAULT NULL,
`eve_mins` double DEFAULT NULL,
`eve_calls` bigint(20) DEFAULT NULL,
`night_mins` double DEFAULT NULL,
`night_calls` bigint(20) DEFAULT NULL,
`int_mins` double DEFAULT NULL,
`int_calls` bigint(20) DEFAULT NULL,
`cust_service_calls` bigint(20) DEFAULT NULL,
`Churn` varchar(2048) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

LOAD DATA FROM S3 's3-us-west-2://auroraworkshopassets/data/mldata/churn.txt'
INTO TABLE churn
=======
# Machine Learning with Amazon Aurora

Machine learning integration with Amazon Aurora currently supports <a href="https://aws.amazon.com/comprehend/" target="_blank">Amazon Comprehend</a> and <a href="https://aws.amazon.com/sagemaker/" target="_blank">Amazon SageMaker</a>. Aurora makes direct and secure calls to SageMaker and Comprehend that don’t go through the application layer. Aurora machine learning is based on the familiar SQL programming language, so you don’t need to build custom integrations, move data around, learn separate tools, or have prior machine learning experience.

This lab contains the following tasks:

1. Setup a sample schema and data for ML labs

This lab requires the following prerequisites:

* [Get Started](/prereqs/environment/) - choose **Yes** for the **Enable Aurora ML Labs?** feature option
* [Connect to the Session Manager Workstation](/prereqs/connect/)

## 1. Setup a sample schema and data for ML labs

If you are not already connected to the Session Manager workstation command line, please connect [following these instructions](/prereqs/connect/). Once connected, run the command below, replacing the ==[clusterEndpoint]== placeholder with the cluster endpoint of your DB cluster. This will connect you to the Aurora Mysql database.

```shell
mysql -h[clusterEndpoint] -u$DBUSER -p"$DBPASS"
```

Execute the following SQL queries to create the `mltest` database and tables, and populate them with data. We will use these tables in subsequent labs for inferences.

```sql
DROP SCHEMA IF EXISTS `mltest`;
CREATE SCHEMA `mltest`;
USE `mltest`;

DROP TABLE IF EXISTS `comments`;
CREATE TABLE `comments` (
 `comment_id` INT AUTO_INCREMENT PRIMARY KEY,
 `comment_text` VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

INSERT INTO `comments` (comment_text) VALUES
("This is very useful, thank you for writing it!"),
("Awesome, I was waiting for this feature."),
("An interesting write up, please add more details."),
("I don’t like how this was implemented."),
("Horrible writing, I have read better books.");

CREATE TABLE `churn` (
 `state` varchar(2048) DEFAULT NULL,
 `acc_length` bigint(20) DEFAULT NULL,
 `area_code` bigint(20) DEFAULT NULL,
 `int_plan` varchar(2048) DEFAULT NULL,
 `vmail_plan` varchar(2048) DEFAULT NULL,
 `vmail_msg` bigint(20) DEFAULT NULL,
 `day_mins` double DEFAULT NULL,
 `day_calls` bigint(20) DEFAULT NULL,
 `eve_mins` double DEFAULT NULL,
 `eve_calls` bigint(20) DEFAULT NULL,
 `night_mins` double DEFAULT NULL,
 `night_calls` bigint(20) DEFAULT NULL,
 `int_mins` double DEFAULT NULL,
 `int_calls` bigint(20) DEFAULT NULL,
 `cust_service_calls` bigint(20) DEFAULT NULL,
 `Churn` varchar(2048) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

LOAD DATA FROM S3 's3-us-east-1://awsauroralabsmy-us-east-1/samples/mldata/churn.txt'
INTO TABLE `churn`
>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
COLUMNS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(state,acc_length,area_code,@dummy1,int_plan,vmail_plan,vmail_msg,day_mins,day_calls,@dummy2,eve_mins,eve_calls,@dummy3,night_mins,night_calls,@dummy4,int_mins,int_calls,@dummy5,cust_service_calls,Churn);
<<<<<<< HEAD

```

Execute the following sql statement. You should be able to see two tables, **churn** and **comments**, as shown in the screenshot. If you don't see the tables rerun the commands.

``` sql
show tables;
```
<span class="image">![Reader Load](/ml/overview/1-tables.png?raw=true)</span>

Exit from the mysql prompt by running command below, before you proceed to the next section.

``` sql
exit
```
=======
```

Verify that the schema was created correctly by running the following command:

```sql
show tables;
```

You should be able to see two tables, **churn** and **comments**, as shown below. If you don't see the tables rerun the commands.

<span class="image">![Reader Load](/ml/overview/1-tables.png?raw=true)</span>

Disconnect from the DB cluster, using:

```sql
quit;
```

You may now proceed to the next labs and integrate Aurora with machine learning services.
>>>>>>> 8c53d6e2beeb879a09ce61ef94b3522f7ad747f0
