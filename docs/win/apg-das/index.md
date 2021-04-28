# Set up Database Activity Streams (DAS)

This lab will show you how to set up and leverage <a href="https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/DBActivityStreams.html" target="_blank">Aurora Database Activity Streams (DAS)</a>. Database sctivity streams provide a near real-time data stream of the database activity in your relational database. When you integrate database activity streams with third-party monitoring tools, you can monitor and audit database activity.

Database Activity Streams have the following limits and requirements:

1. Currently, these streams are supported only with Aurora with PostgreSQL compatibility version 2.3, which is compatible with PostgreSQL version 10.7.
2. They require use of AWS Key Management Service (AWS KMS) because the activity streams are always encrypted.

This lab contains the following tasks:

1. Create an AWS KMS customer managed key (CMK)
2. Configure Database Activity Streams
3. Generate database load
4. Read activity from the stream
5. Stop the activity stream

This lab requires the following prerequisites:

* [Get Started](/win/)
* [Connect to your Aurora PostgreSQL DB cluster](/win/apg-connect/)



## 1. Create an AWS KMS customer managed key (CMK)

Database activity streams require a master key to encrypt the data key that in turn encrypts the database activity logged (see <a href="https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html#enveloping" target="_blank">envelope encryption</a>). The default Amazon RDS master key can’t be used as the master key for DAS. Therefore, you need to create a new AWS KMS customer managed key (CMK) to configure the DAS.

Open the <a href="https://eu-west-1.console.aws.amazon.com/kms/home?region=eu-west-1#/kms/home" target="_blank">AWS Key Management Service (KMS) console</a>. Click **Create a key**.

<span class="image">![KMS Home](kms-home.png?raw=true)</span>

On the next screen under **Configure key** choose `Symmetric` for **Key type** and click **Next**.

<span class="image">![KMS Configure](kms-configure.png?raw=true)</span>

In the **Create alias and description** section, name the key `auroralab-postgres-das`. Provide the following description of the key:

```text
Amazon Aurora lab, CMK for Aurora PostgreSQL Database Activity Streaming (DAS)
```

Then, click **Next**.

<span class="image">![KMS Labels](kms-labels.png?raw=true)</span>

In the **Key administrators** section, select `TeamRole` and `OpsRole` as an administrator (you can search for the names to find them quicker). Check the box next to `TeamRole` and `OpsRole` click **Next**.

<span class="image">![KMS Administrators](kms-admins.png?raw=true)</span>

Similarly to above, in the section named **This account** select the `auroralab-bastion-[region]`, `TeamRole` and `OpsRole` IAM roles, check the box next to them, and click **Next**.

Review the policy for accuracy and click **Finish**.

<span class="image">![KMS Review](kms-review.png?raw=true)</span>

Verify the newly created KMS key on the KMS dashboard.

<span class="image">![KMS Listing](kms-listing.png?raw=true)</span>


## 2. Configure Database Activity Streams

You start an activity stream at the DB cluster level to monitor database activity for all DB instances of the cluster. Any DB instances added to the cluster are also automatically monitored.

You can choose to have the database session handle database activity events either synchronously or asynchronously:

Mode | Use case | Description
--- | --- | ---
Synchronous | The synchronous mode favors the accuracy of the activity stream over database performance. | In synchronous mode, when a database session generates an activity stream event, the session blocks until the event is made durable. If the event can't be made durable for some reason, the database session returns to normal activities. However, an RDS event is sent indicating that activity stream records might be lost for some time. A second RDS event is sent after the system is back to a healthy state.
Asynchronous | Asynchronous mode favors database performance over the accuracy of the activity stream. | In asynchronous mode, when a database session generates an activity stream event, the session returns to normal activities immediately. In the background, the activity stream event is made a durable record. If an error occurs in the background task, an RDS event is sent. This event indicates the beginning and end of any time windows where activity stream event records might have been lost.

Open the <a href="https://eu-west-1.console.aws.amazon.com/rds/home?region=eu-west-1#database:id=auroralab-postgres-cluster;is-cluster=true" target="_blank">Amazon RDS service console at the cluster details page</a>. If you navigated to the RDS console by other means, click on the `auroralab-postgres-cluster` in the **Databases** section of the console.

From the **Actions** dropdown button, choose **Start activity stream**. The **Database Activity Stream** setup window appears:

<span class="image">![RDS Cluster Details](rds-cluster-detail-action.png?raw=true)</span>

Set the **Master key**, to the alias of the CMK created previously (named `auroralab-postgres-das`). Choose either **Asynchronous** or **Synchronous** based on preference. Choose **Apply immediately**, then click **Continue**.

<span class="image">![RDS Enable DAS](rds-das-confirm.png?raw=true)</span>

The **Status** column for the DB cluster will start showing **configuring-activity-stream**. Please wait until the cluster becomes **Available** again. You may need to refresh the browser page to get the latest status timely.

<span class="image">![RDS Cluster Configuring](rds-cluster-configuring.png?raw=true)</span>

Verify that DAS is enabled by clicking on the cluster named `auroralab-postgres-cluster` and toggle to the **Configuration** tab.

<span class="image">![RDS Cluster Configuration Details](rds-cluster-config-pane.png?raw=true)</span>

Note the **Resource id** and **Kinesis stream** values, you will need these value further in this lab.


## 3. Generate database load

You will generate load on the database using the **pgbench** tool and then access the database activity produced by the load generator.

If you are not already connected to the Session Manager workstation command line, please connect [following these instructions](/win/apg-connect/). Start the pgbench tool using the following sequence of commands, replacing the ==[postgresClusterEndpoint]== placeholder with the Cluster endpoint retrieved from the Team Dashboard web page (see [Connect to Aurora PostgreSQL](/win/apg-connect/)). You will also need to provide the password retrieved from the secret in AWS Secrets Manager (see [Connect to Aurora PostgreSQL](/win/apg-connect/)):

```shell
pgbench  --progress-timestamp -M prepared -n -T 60 -P 1  -c 5  --host=[postgresClusterEndpoint] -b tpcb-like@1 -b select-only@20 --username=masteruser mylab
```


## 4. Read activity from the stream

A python script with sample code to read the activity stream has already been saved on your EC2 workstation at this location `/home/ec2-user/das-script.py`.

You will be required to update the script, changing the following constants (lines 14 through 16) to reflect the values in your environment:

Constant | Value
--- | ---
**REGION_NAME** | `eu-west-1`
**RESOURCE_ID** | See the cluster **Resource id** at the end of step **2. Configure Database Activity Streams** above.
**STREAM_NAME** | See the **Kinesis stream** name at the end of step **2. Configure Database Activity Streams** above.

You can edit the script using the following command:

```shell
nano das-script.py
```

Once you have finished making changes, save the script by pressing `Ctrl+X`, then typing `y` followed by `<enter>` to confirm.

??? tip "How to create your own python script code"
    You can also copy and paste the script text below to create a new python file and replace the values of the relevant constants, according to the table above.

    ```shell
    vi das_script.py
    ```

    ```python
    import zlib
    import boto3
    import base64
    import json
    import time
    import aws_encryption_sdk
    from Crypto.Cipher import AES
    from aws_encryption_sdk import DefaultCryptoMaterialsManager
    from aws_encryption_sdk.internal.crypto import WrappingKey
    from aws_encryption_sdk.key_providers.raw import RawMasterKeyProvider
    from aws_encryption_sdk.identifiers import WrappingAlgorithm, EncryptionKeyType



    REGION_NAME = 'eu-west-1'                    # us-east-1
    RESOURCE_ID = 'cluster-KSBSDVYL5I3ADAJGBFINGWEH7Y'      # cluster-ABCD123456
    STREAM_NAME = 'aws-rds-das-cluster-KSBSDVYL5I3ADAJGBFINGWEH7Y' # aws-rds-das-cluster-ABCD123456


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
            shard_iter_response = kinesis.get_shard_iterator(StreamName=STREAM_NAME, ShardId=shard['ShardId'],
                                                             ShardIteratorType='TRIM_HORIZON') # TRIM_HORIZON will display all messages
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
                    time.sleep(0.1)
            shard_iters = next_shard_iters


    if __name__ == '__main__':
        main()
    ```

Once you have updated the script with the correct values (or created a new one), run the python script (either `das-script.py` or `das_script.py` depending on whether you created it from scratch) in the command line:

```shell
python das-script.py
```

The script will read one record from the stream, and print it out on the command line, you can use a tool, such as <a href="https://jsonformatter.org/" target=_blank">jsonformatter.org</a>, to format the JSON structure to be more readable.

<span class="image">![1-das-55](1-das-55.png?raw=true)</span>

Your output should look similar to the following example:

```json
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

## 5. Stop the activity stream

Open the <a href="https://eu-west-1.console.aws.amazon.com/rds/home?region=eu-west-1#database:id=labstack-postgres-cluster;is-cluster=true" target="_blank">Amazon RDS service console at the cluster details page</a>, if not already open. If the cluster is not already selected, choose **Databases** and click on the DB identifier with the cluster named `auroralab-postgres-cluster`.

Click on the **Actions** dropdown, and select **Stop activity stream**.

<span class="image">![RDS Cluster Stop](rds-cluster-detail-stop.png?raw=true)</span>

On the setup screen choose **Apply immediately** and click **Continue**.

<span class="image">![RDS DAS Stop](rds-das-stop.png?raw=true)</span>

The status column on the RDS Database home page for the cluster will start showing `configuring-activity-stream`.
