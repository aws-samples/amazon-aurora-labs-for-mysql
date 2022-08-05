"""
Amazon Aurora Labs for MySQL
This scripts will allow you to test accesing the cluster using a secret in AWS Secrets Manager

Dependencies:
none

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
"""

# Dependencies
import sys
import argparse
import datetime
import time
import socket
import random
import pymysql
import math
import json
from os import environ
from os import system
from prettytable import PrettyTable
import urllib3
import boto3
import base64
from botocore.exceptions import ClientError


# Define parser
parser = argparse.ArgumentParser()
parser.add_argument('-s', '--secret-name', help="The name of the secret", required=True)
args = parser.parse_args()

# Track this lab for usage analytics, if user has explicitly or implicitly agreed
def track_analytics():
    http = urllib3.PoolManager()
    if environ["AGREETRACKING"] == 'Yes':
        # try/catch
        try:
            # build tracker payload
            payload = {
                'stack_uuid': environ["STACKUUID"],
                'stack_name': environ["STACKNAME"],
                'stack_region': environ["STACKREGION"],
                'deployed_cluster': None,
                'deployed_ml':  None,
                'deployed_gdb': None,
                'is_secondary': None,
                'event_timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                'event_scope': 'Script',
                'event_action': 'Execute',
                'event_message': 'db_access_test.py',
                'ee_event_id': None,
                'ee_team_id': None,
                'ee_module_id': None,
                'ee_module_version': None
            }

            # Send the tracking data
            r = http.request('POST', environ["ANALYTICSURI"], body=json.dumps(payload).encode('utf-8'), headers={'Content-Type': 'application/json'})
        except Exception as e:
            # Errors in tracker interaction should not prevent operation of the function in critical path
            print("[ERROR]", e)


def get_secret(secret_name):
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )

    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'AccessDeniedException':
            # We don't have access to retieve the secret value.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
    else:
        # Decrypts secret using the associated KMS key.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            return get_secret_value_response['SecretString']
        else:
            return base64.b64decode(get_secret_value_response['SecretBinary'])
            
    return None


# Perform some database actions
def perform_actions_on_db(conn):
    item_count = 0
    with conn.cursor() as cur:
        cur.execute(
            "CREATE TABLE Employee ( EmpID int NOT NULL, Name varchar(255) NOT NULL, PRIMARY KEY (EmpID))"
        )
        print("Created table in Aurora MySQL database")
        cur.execute('INSERT INTO Employee (EmpID, Name) VALUES (1, "Joe")')
        cur.execute('INSERT INTO Employee (EmpID, Name) VALUES (2, "Bob")')
        cur.execute('INSERT INTO Employee (EmpID, Name) VALUES (3, "Mary")')
        conn.commit()
        cur.execute("SELECT * FROM Employee")
        for row in cur:
            item_count += 1
            print(row)
        conn.commit()
        print("Added %d items to Aurora MySQL table" % (item_count))
        cur.execute("DROP TABLE Employee")
    conn.commit()
    print("Dropped table from Aurora MySQL database")


# Invoke tracking function
track_analytics()

try:
    # retrieve secret
    secret = get_secret(args.secret_name)
    if not secret:
        sys.exit(f"\nCould not retrieve secret for: '{args.secret_name}'")
    # deserialze the json string
    secret = json.loads(secret)
    
    # set the ssl to allow secured connection
    ssl = {"ca": "rds-combined-ca-bundle.pem"}

    # Connect to the desired endpoint
    conn = pymysql.connect(host=secret['host'], user=secret['username'], password=secret['password'], database='mylab', ssl=ssl, autocommit=True, connect_timeout=10)

    # do something on the database
    perform_actions_on_db(conn)

# Deal with MySQL connection errors
except pymysql.MySQLError as e:
    # Get the error code and message
    error_code = e.args[0]
    error_message = e.args[1]
    
    # Display error
    print("[ERROR]", "%s, MySQL Error %d: %s" % (time.strftime('%H:%M:%S %Z'), error_code, error_message))
    sys.exit("\nUnexpected MySQL error encountered")

# Any other error bail out
except:
    print(sys.exc_info()[1])
    sys.exit("\nUnexpected error encountered.")
