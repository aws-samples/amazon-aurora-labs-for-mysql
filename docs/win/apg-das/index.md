# Database Activity Streaming

## 1. Prerequisite

!!! note
    If you started with module - "Creating a New Aurora Cluster" please skip to the next step/section as you have already created the EC2 key pair which  you can use for this lab.

### 1.1 **Create an EC2 Key Pair**: <br>

You will need an EC2 key pair in order to log into the EC2 bastion instance<br>

To create a new key pair:

1. Open the EC2 service console
2. In the left-hand gutter under “Network & Security” click “Key Pairs”
3. Supply a name and click “Create”
4. Download or otherwise save the .pem file

### 1.2  **Create KMS Key**: <br>

Database Activity Streaming requires the Master Key to encrypt the key that in turn encrypts the database activity logged. The Default AWS RDS KMS key can’t be used as the Master key. Therefore, we need to create a new customer managed KMS key to configure the Database Activity Streaming.

On the AWS console search for KMS and click on Key Management Service. Select the Customer Managed Keys on the left-hand side and click on Create Key

<span class="image">![1-kms-1](1-kms-1.png?raw=true)</span><br>
<span class="image">![1-kms-3](1-kms-2.png?raw=true)</span><br>
<span class="image">![1-kms-3](1-kms-3.png?raw=true)</span><br>

On the next screen under Configure key choose Symmetric key type and click Next

<span class="image">![1-kms-4](1-kms-4.png?raw=true)</span><br>


On the next screen under Add Labels give the name for the key under the field Alias such as cmk-apg-lab

Under Description field type a description for the key such as Customer managed Key for Aurora PostgreSQL Database Activity Streaming (DAS) lab and click Next

<span class="image">![1-kms-5](1-kms-5.png?raw=true)</span><br>

On the next screen under the Key Administrators search for the account name (IAM user) you are using to connect to the AWS console. The IAM user name can be seen on the top right-hand side of the console. In this case the IAM user name is TeamRole. Check the box with the IAM user and click Next.

<span class="image">![1-kms-6](1-kms-6.png?raw=true)</span><br>

On the next screen under the Define Key usage permissions search for the account name (IAM user) you are using to connect to the AWS console. The IAM user name can be seen on the top right-hand side of the console. In this case the IAM user name is TeamRole. Check the box with the IAM user and click Next.

<span class="image">![1-kms-7](1-kms-7.png?raw=true)</span><br>

On the next screen review the policy and click Finish

<span class="image">![1-kms-8](1-kms-8.png?raw=true)</span><br>

Verify the newly created KMS key on the KMS dashboard 

<span class="image">![1-kms-9](1-kms-9.png?raw=true)</span><br>


## 2. Creating Aurora PostgreSQL cluster with Cloudformation

!!! note
    if you started the lab with module "Creating a New Aurora Cluster" please skip the section -2 and proceed to the next section as you have already created the Aurora PostgreSQL cluster.

1. <a href="https://us-west-2.console.aws.amazon.com/cloudformation/home?region=us-west-2" target="_blank">Log in to your AWS console and go to the CloudFormation landing page</a>
2.      Click create stack, select ‘Specify an Amazon S3 template URL’ and launch the CloudFormation stack from this <a href="https://tinyurl.com/my-cf-template" target="_blank">template</a>
3.      Download and save this locally and use upload a template to S3 option and click on “Choose File” option to point to the location where you have saved the template.
4.      Here is a screenshot of the first page –
<span class="image">![1-das-cf1](1-das-cf1.png?raw=true)</span>
<br>
<span class="image">![1-das-cf2](1-das-cf2.png?raw=true)</span><br>
<span class="image">![1-das-cf3](1-das-cf3.png?raw=true)</span><br>
<span class="image">![1-das-cf4](1-das-cf4.png?raw=true)</span><br>
<span class="image">![1-das-cf5](1-das-cf5.png?raw=true)</span><br>
<span class="image">![1-das-cf6](1-das-cf6.png?raw=true)</span><br>
<span class="image">![1-das-cf7](1-das-cf7.png?raw=true)</span><br>
<span class="image">![1-das-cf8](1-das-cf8.png?raw=true)</span><br>
<span class="image">![1-das-cf9](1-das-cf9.png?raw=true)</span><br>
<span class="image">![1-das-cf10](1-das-cf10.png?raw=true)</span><br>
<span class="image">![1-das-cf11](1-das-cf11.png?raw=true)</span><br>
<span class="image">![1-das-cf12](1-das-cf12.png?raw=true)</span><br>

### 2.1 Retrieving Database credentials from Secret Manager

1. Search for the secret name as shown in the output of the stack and select the secret name.
<span class="image">![1-das-secrets-1](1-das-secrets-1.png?raw=true)</span><br>

2. Click on the Retrieve secret value to get the Database user and the password to connect to the Aurora Database.
<span class="image">![1-das-secrets-2](1-das-secrets-2.png?raw=true)</span><br>
<span class="image">![1-das-secrets-3](1-das-secrets-3.png?raw=true)</span><br>
<span class="image">![1-das-secrets-4](1-das-secrets-4.png?raw=true)</span><br>

###2.2 Cloudformation Resource chart

Please note that the Database names and the Custom Cluster and Database Parameter groups shown below are only for illustrative purpose. Participants are required to use the appropriate resources created from the Cloudformation template.

**Please refer the below table for the list of resources and the value**

Resource name | Value
--- | ---
Cluster Parameter Group | refer CloudFormation template output section and refer the key value “apgcustomclusterparamgroup”
Database Parameter Group | refer CloudFormation template output section and refer the key value “apgcustomdbparamgroup”
Cluster Endpoint |      refer CloudFormation template output section and refer the key value “clusterEndpoint”
Reader Endpoint | refer CloudFormation template output section and refer the key value “readerEndpoint”
DB name | mylab
DB username     | masteruser
DB password     | extract from the secrets Manager as shown above
bastionEndpoint | refer CloudFormation template output section and refer the key value “bastionEndpoint”

### 2.3 Connecting to the EC2 bastion Instance with Systems Manager

!!! note
    We recommend using AWS Systems Manager to connect to the EC2 Instance as Session Manager provides secure and auditable instance management without the need to open inbound ports, maintain bastion hosts, or manage SSH keys. If you preferred to use EC2 Instance using SSH key access then proceed to section 2.4 instead

!!! warning "Region Check"
    Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.

1. Connect to your workstation instance

Open the Systems Manager: Session Manager service console. Click **Configure Preferences**.



Ensure you are still working in the correct region, especially if you are following the links above to open the service console at the right screen.



On the AWS console search for Systems Manager and click on **Systems Manager** Service. Select the **Session Manager** on the left-hand side.

<span class="image">![1-ssm1_1](../prerequisites/ssm1_1.png?raw=true)</span><br>

<span class="image">![1-ssm1_2](../prerequisites/ssm1_2.png?raw=true)</span><br>

Click on the Start session 

<span class="image">![1-ssm1_3](../prerequisites/ssm1_3.png?raw=true)</span><br>

Click on **Start session**

Select the Instance name which was created part of the Cloudformation template, the name of the Instance has the naming convention <Stack name-bastion-host> 

<span class="image">![1-ssm1_4](../prerequisites/ssm1_4.png?raw=true)</span><br>

Click on **Start session** again to go the EC2 instance screen.



By default the system manager connects as **ssmuser** . All the lab work has been performed as **ec2-user** . We need to switch to the **ec2-user** 
```
sh-4.2$ whoami
ssm-user
sh-4.2$ sudo su -
Last login: Thu Feb 27 02:28:24 UTC 2020 on pts/1
[root@ip-x.x.x.x ~]# su - ec2-user
Last login: Wed Feb 26 18:04:46 UTC 2020 on pts/0
[ec2-user@x.x.x.x ~]$ whoami
ec2-user
```
<span class="image">![1-ssm1_5](../prerequisites/ssm1_5.png?raw=true)</span><br>
### 2.4 Connecting to the EC2 bastion Instance 

We are creating EC2 instance (Amazon Linux AMI-ID ami-0f2176987ee50226e) and bootstrapping the EC2 Instance to have pgbench and sysbench benchmarking tools to be installed.

```
ssh -i <keypair.pem> ec2-user@<bastionEndpoint>
```

Replace the [`keypair.pem`] with the keypair file name input provided to the Cloud formation template. Replace the “bastionEndpoint” with the key value from the output section of the Cloud formation template.

If you need to open an access for your laptop IP specifically, then whitelist your IP, by specifying your IP in the format `x.x.x.x/32` (<a href=" http://www.whatsmyip.org/" target="_blank">Lookup your IP </a>). If there are any issues in accessing the instance, you can always modify the security group to populate your IP address as My IP as mentioned <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/authorizing-access-to-an-instance.html" target="_blank"> here</a>.

##3 Database Activity Streams 
Database Activity Streams provide a near real-time data stream of the database activity in your relational database. When you integrate Database Activity Streams with third-party monitoring tools, you can monitor and audit database activity. 

Database Activity Streams have the following limits and requirements:

1. Currently, these streams are supported only with Aurora with PostgreSQL compatibility version 2.3, which is compatible with PostgreSQL version 10.7. 
2. They require use of AWS Key Management Service (AWS KMS) because the activity streams are always encrypted. 

###3.1 Configuring Database Activity Streams

You start an activity stream at the DB cluster level to monitor database activity for all DB instances of the cluster. Any DB instances added to the cluster are also automatically monitored. 

You can choose to have the database session handle database activity events either synchronously or asynchronously: 

1. Synchronous mode – In synchronous mode, when a database session generates an activity stream event, the session blocks until the event is made durable. If the event can't be made durable for some reason, the database session returns to normal activities. However, an RDS event is sent indicating that activity stream records might be lost for some time. A second RDS event is sent after the system is back to a healthy state. 
***The synchronous mode favors the accuracy of the activity stream over database performance. ***
2. Asynchronous mode – In asynchronous mode, when a database session generates an activity stream event, the session returns to normal activities immediately. In the background, the activity stream event is made a durable record. If an error occurs in the background task, an RDS event is sent. This event indicates the beginning and end of any time windows where activity stream event records might have been lost. 
***Asynchronous mode favors database performance over the accuracy of the activity stream.*** 

###3.2 To start an activity stream

1. Open the <a href="https://us-west-2.console.aws.amazon.com/rds/home?region=us-west-2" target="_blank">Amazon RDS service console</a>.<br>
2. In the navigation pane, choose Databases and click on the DB identifier with the cluster name you created as a part of the CloudFormation stack.
<span class="image">![1-das-stream-1](1-das-stream-1.png?raw=true)</span><br>
3. For Actions, choose Start activity stream. The Database Activity Stream window appears. 
<span class="image">![1-das-stream-2](1-das-stream-2.png?raw=true)</span><br>
4. Enter the following settings in the Database Activity Stream window: 

	a. For Master key, choose a key from the list of AWS KMS keys. 

	b. For Database activity stream mode, choose Asynchronous or Synchronous. 

	c. Choose Apply immediately. 

5. When you're done entering settings, choose Continue. 
<span class="image">![1-das-51](1-das-51.png?raw=true)</span><br>
6. The status column on the RDS-> Database page for the cluster will start showing `configuring-activity-stream`
<span class="image">![1-das-52](1-das-52.png?raw=true)</span><br>
7. Verify the activity streaming by clicking on the cluster name `(with role =regional)` and click on configuration.
<span class="image">![1-das-53](1-das-53.png?raw=true)</span><br>

###3.3 Accessing Database Activity Streams

We are generating load on the Database via pgbench and will access the database activity in real time. We will connect to the EC2 Instance to generate the load on the Database and will access the Database activity streaming information from another session by execution the python script `(das_qpm.py)`. 

We will be formatting the output of the 1 streaming record using JSON formatter.
```
export PATH=/home/ec2-user/postgresql-10.7/src/bin/pgbench:$PATH

cd /home/ec2-user/postgresql-10.7/src/bin/pgbench

./pgbench -i --fillfactor=90 --scale=100 --host=labstack-cluster.cluster-xxxxxxxxx.us-west-2.rds.amazonaws.com --username=masteruser mylab

./pgbench --host=labstack-cluster.cluster-xxxxxxxxx.us-west-2.rds.amazonaws.com --username=masteruser --protocol=prepared -P 60 --time=300 --client=16 --jobs=96 mylab> results1.log
```
###3.4 Sample code Database Activity Streams

The python file with the sample code is already created by the CloudFormation script at this location `/home/ec2-user/das-script.py`. You will be required to replace the value for `RESOURCE_ID` with the `Resourceid` value from your cluster configuration as shown below and also replace the value for `STREAM_NAME` with the `Kinesis Stream`. 

You can also copy and paste the script text as shown below to create a new python file and replace the value for `RESOURCE_ID` with the `Resourceid` value from your cluster configuration as shown below and also replace the value for `STREAM_NAME` with the `Kinesis Stream`. 
<span class="image">![1-das-53](1-das-53.png?raw=true)</span><br>

```
vi das_script.py
```
```
import zlib
import boto3
import base64
import json
import aws_encryption_sdk
from Crypto.Cipher import AES
from aws_encryption_sdk import DefaultCryptoMaterialsManager
from aws_encryption_sdk.internal.crypto import WrappingKey
from aws_encryption_sdk.key_providers.raw import RawMasterKeyProvider
from aws_encryption_sdk.identifiers import WrappingAlgorithm, EncryptionKeyType

REGION_NAME = 'us-west-2'                    
RESOURCE_ID = 'cluster-XXXXXXXXXXX'      # cluster-ABCD123456
STREAM_NAME = 'aws-rds-das-cluster-XXXXXXXXXXX' # aws-rds-das-cluster-ABCD123456

class MyRawMasterKeyProvider(RawMasterKeyProvider):
    provider_id = "BC"

    def __new__(cls, *args, **kwargs):
        obj = super(RawMasterKeyProvider, cls).__new__(cls)
        return obj

    def __init__(self, plain_key):
        RawMasterKeyProvider.__init__(self)
        self.wrapping_key = WrappingKey(wrapping_algorithm=WrappingAlgorithm.AES_256_GCM_IV12_TAG16_NO_PADDING,
                                        wrapping_key=plain_key, wrapping_key_type=EncryptionKeyType.SYMMETRIC)

    def _get_raw_key(self, key_id):
        return self.wrapping_key


def decrypt_payload(payload, data_key):
    my_key_provider = MyRawMasterKeyProvider(data_key)
    my_key_provider.add_master_key("DataKey")
    decrypted_plaintext, header = aws_encryption_sdk.decrypt(
        source=payload,
        materials_manager=aws_encryption_sdk.DefaultCryptoMaterialsManager(master_key_provider=my_key_provider))
    return decrypted_plaintext


def decrypt_decompress(payload, key):
    decrypted = decrypt_payload(payload, key)
    return zlib.decompress(decrypted, zlib.MAX_WBITS + 1)


def main():
    session = boto3.session.Session()
    kms = session.client('kms', region_name=REGION_NAME)
    kinesis = session.client('kinesis', region_name=REGION_NAME)

    response = kinesis.describe_stream(StreamName=STREAM_NAME)
    shard_iters = []
    for shard in response['StreamDescription']['Shards']:
        shard_iter_response = kinesis.get_shard_iterator(StreamName=STREAM_NAME, ShardId=shard['ShardId'],ShardIteratorType='LATEST') # TRIM_HORIZON will 
        shard_iters.append(shard_iter_response['ShardIterator'])

    while len(shard_iters) > 0:
        next_shard_iters = []
        for shard_iter in shard_iters:
            response = kinesis.get_records(ShardIterator=shard_iter, Limit=10000)
            for record in response['Records']:
                record_data = record['Data']
                record_data = json.loads(record_data)
                payload_decoded = base64.b64decode(record_data['databaseActivityEvents'])
                data_key_decoded = base64.b64decode(record_data['key'])
                data_key_decrypt_result = kms.decrypt(CiphertextBlob=data_key_decoded,
                                                      EncryptionContext={'aws:rds:dbc-id': RESOURCE_ID})
                print decrypt_decompress(payload_decoded, data_key_decrypt_result['Plaintext'])
            if 'NextShardIterator' in response:
                next_shard_iters.append(response['NextShardIterator'])
        shard_iters = next_shard_iters

if __name__ == '__main__':
    main()

```
```
python das_script.py
```
###3.5 Sample Output Activity Streaming
<a href="https://jsonformatter.org/" target=_blank"> jsonformatter.org</a>
<span class="image">![1-das-55](1-das-55.png?raw=true)</span><br>
```
{
  "type": "DatabaseActivityMonitoringRecord",
  "clusterId": "cluster-XXXXXXXXXXXXXXXXXXXXXXXXXX",
  "instanceId": "db-XXXXXXXXXXXXXXXXXXXXXXX",
  "databaseActivityEventList": [
    {
      "logTime": "2019-12-26 06:56:09.090054+00",
      "statementId": 3731,
      "substatementId": 1,
      "objectType": "TABLE",
      "command": "INSERT",
      "objectName": "public.pgbench_history",
      "databaseName": "mylab",
      "dbUserName": "masteruser",
      "remoteHost": "10.0.0.204",
      "remotePort": "33948",
      "sessionId": "5e04596c.2383",
      "rowCount": 1,
      "commandText": "INSERT INTO pgbench_history (tid, bid, aid, delta, mtime) VALUES ($1, $2, $3, $4, CURRENT_TIMESTAMP);",
      "paramList": [
        "424",
        "62",
        "1788678",
        "-2770"
      ],
      "pid": 9091,
      "clientApplication": "pgbench",
      "exitCode": null,
      "class": "WRITE",
      "serverVersion": "2.3.5",
      "serverType": "PostgreSQL",
      "serviceName": "Amazon Aurora PostgreSQL-Compatible edition",
      "serverHost": "10.0.12.39",
      "netProtocol": "TCP",
      "dbProtocol": "Postgres 3.0",
      "type": "record"
    }
  ]
}
```
###3.6 Stop the Database Activity Streaming

1. In the navigation pane, choose Databases and click on the DB identifier with the cluster name you created as a part of the CloudFormation stack.
<span class="image">![1-das-56](1-das-56.png?raw=true)</span><br>
2. Click on “Actions” and select “stop activity stream” and click “continue to stop Database activity streaming on the cluster.
<span class="image">![1-das-57](1-das-57.png?raw=true)</span><br>
<span class="image">![1-das-58](1-das-58.png?raw=true)</span><br>
3. The status column on the RDS Database home page for the cluster will start showing “configuring-activity-stream”
<span class="image">![1-das-59](1-das-59.png?raw=true)</span><br>

