import zlib
import boto3
import base64
import json
import time
import sys
import aws_encryption_sdk
from Crypto.Cipher import AES
from aws_encryption_sdk import DefaultCryptoMaterialsManager
from aws_encryption_sdk.internal.crypto import WrappingKey
from aws_encryption_sdk.key_providers.raw import RawMasterKeyProvider
from aws_encryption_sdk.identifiers import WrappingAlgorithm, EncryptionKeyType
from os import environ
import urllib3
import argparse
import datetime



parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region_name', help="The AWS region")
parser.add_argument('-i', '--resource_id', help="The resource id from the cluster")
parser.add_argument('-s', '--stream_name', help="The stream name from the cluster")
args = parser.parse_args()

REGION_NAME = args.region_name
RESOURCE_ID = args.resource_id
STREAM_NAME = args.stream_name

#REGION_NAME = 'eu-west-1'                    # us-east-1
#RESOURCE_ID = 'cluster-KSBSDVYL5I3ADAJGBFINGWEH7Y'      # cluster-ABCD123456
#STREAM_NAME = 'aws-rds-das-cluster-KSBSDVYL5I3ADAJGBFINGWEH7Y' # aws-rds-das-cluster-ABCD123456


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

def track_analytics():
    http = urllib3.PoolManager()
    if environ["AGREETRACKING"] == 'Yes':
                # try/catch
        try:
                  # track analytics
            payload = {
                    'stack_uuid': None, #environ["STACKUUID"]#
                    'stack_name': environ["STACKNAME"],
                    'stack_region': environ["STACKREGION"],
                    'deployed_cluster': None,
                    'deployed_ml':  None,
                    'deployed_gdb': None,
                    'is_secondary': None,
                    'event_timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                    'event_scope': 'Script',
                    'event_action': 'Database Activity Script',
                    'event_message': 'Ran Database Activity Reader script',
                    'ee_event_id': None,
                    'ee_team_id': None,
                    'ee_module_id': None,
                    'ee_module_version': None
                  }

            r = http.request('POST', environ["ANALYTICSURI"], body=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
                  #print("[INFO]", "Event tracking for UUID:", payload["stack_uuid"])
        except Exception as e:
                  # errors in tracker interaction should not prevent operation of the function in critical path
            print("[ERROR]", e)
    else:
        print("[INFO]", "Opted out of analytics")

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
    track_analytics()
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
                print (decrypt_decompress(payload_decoded, data_key_decrypt_result['Plaintext']))
            if 'NextShardIterator' in response:
                next_shard_iters.append(response['NextShardIterator'])
                time.sleep(0.1)
        shard_iters = next_shard_iters


if __name__ == '__main__':
   main()