# Machine Learning on Amazon Aurora 

Machine Learning integration with Amazon aurora currently supports Comprehend and Sagemaker. We will follow steps in this lab to create and run functions that will seemlessly and securly call Comprehend and Sagemaker in the background.

## Pre-requisits
Before running the lab make sure you have met the followin pre-requisits.

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
COLUMNS TERMINATED BY ','
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(state,acc_length,area_code,@dummy1,int_plan,vmail_plan,vmail_msg,day_mins,day_calls,@dummy2,eve_mins,eve_calls,@dummy3,night_mins,night_calls,@dummy4,int_mins,int_calls,@dummy5,cust_service_calls,Churn);

```

Execute the following sql statement. You should be able to see two tables, **churn** and **comments**, as shown in the screenshot. If you don't see the tables rerun the commands.

``` sql
show tables;
```
<span class="image">![Reader Load](1-tables.png?raw=true)</span>

Exit from the mysql prompt by running command below, before you proceed to the next section.

``` sql
exit
```
