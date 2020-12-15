"""
Amazon Aurora Labs for MySQL
Simple Aurora DB cluster failover monitoring script, leveraging only the DNS endpoints. This scripts
connects to the database using the cluster endpoint, approx. once a second and checks the role of
the database engine. If it cannot connect or it connects to a reader instead, it counts the elapsed time.

Changelog:
2019-10-28 - Initial release

Dependencies:
none

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
"""

# Dependencies
import sys
import argparse
import time
import socket
import random
import pymysql
import datetime
import json
import urllib3
from os import environ

# Define parser
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--endpoint', help="The database endpoint", required=True)
parser.add_argument('-p', '--password', help="The database user password", required=True)
parser.add_argument('-u', '--username', help="The database user name", required=True)
args = parser.parse_args()

# Instructions
print("Press Ctrl+C to quit this test...")

# Global variables
initial = True
failover_detected = False
failover_start_time = None

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
                'event_message': 'simple_failover.py',
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


# Invoke tracking function
track_analytics()

# Loop Indefinitely
while True:
    try:
        # Resolve the endpoint
        host = socket.gethostbyname(args.endpoint)

        # Take timestamp
        conn_start_time = time.time()

        # Connect to the cluster endpoint
        conn = pymysql.connect(host=args.endpoint, user=args.username, password=args.password, database='information_schema', autocommit=True, connect_timeout=1)

        # Query status
        sql_command = "SELECT @@innodb_read_only, @@aurora_server_id, @@aurora_version;"

        # Run the query
        with conn.cursor() as cursor:
            cursor.execute(sql_command)
            (is_reader, server_id, version) = cursor.fetchone()
            if is_reader > 0:
                server_role = "reader"
            else:
                server_role = "writer"
            cursor.close()

        # Take timestamp
        conn_end_time = time.time()

        # Close the connection
        conn.close()

        # Connected to a reader from the get go?
        if initial and is_reader > 0:
            raise Exception("You have connected to a reader endpoint, try connecting to the cluster endpoint instead.")

        # In the middle of a failover?
        if failover_detected:
            if is_reader > 0:
                # Display error
                print("[ERROR]", "%s: connected to reader (%s), DNS is stale!" % (time.strftime('%H:%M:%S %Z'), server_id))
            else:
                # Take timestamp
                failover_detected = False
                failover_end_time = conn_end_time

                # Display success
                print("[SUCCESS]", "%s: failover completed, took: ~ %d sec., connected to %s (%s, %s)" % (time.strftime('%H:%M:%S %Z'), (failover_end_time - failover_start_time), server_id, server_role, version))
        else:
            if is_reader > 0:
                # Detect failover
                failover_start_time = conn_start_time
                failover_detected = True

                # Display error
                print("[ERROR]", "%s: connected to reader (%s), DNS is stale!" % (time.strftime('%H:%M:%S %Z'), server_id))
            else:
                # Display info
                print("[INFO]", "%s: connected to %s (%s, %s)" % (time.strftime('%H:%M:%S %Z'), server_id, server_role, version))

        # No longer in the initial loop
        initial = False;

        # Wait 1 second
        time.sleep(1)

    # Trap keyboard interrupt, exit
    except KeyboardInterrupt:
        sys.exit("\nStopped by the user")

    # Deal with MySQL connection errors
    except pymysql.MySQLError as e:
        # Get the error code and message
        error_code = e.args[0]
        error_message = e.args[1]

        # Can't connect, assume failover
        if error_code == 2003 or error_code == 2005 or error_code == 2006 or error_code == 2013:
            # Detect failover
            if not failover_detected:
                failover_start_time = conn_start_time
            failover_detected = True

            # Display error
            print("[ERROR]", "%s: can't connect to the database (MySQL error: %d)!" % (time.strftime('%H:%M:%S %Z'), error_code))

            # Wait 1 second
            time.sleep(1)

        # Connected to a proxy
        elif error_code == 1105 and args.endpoint.find('.proxy-') > 0:
            # Detect failover
            if not failover_detected:
                failover_start_time = conn_start_time
            failover_detected = True

            # Display error
            print("[ERROR]", "%s: can't connect to the database (MySQL error: %d)!" % (time.strftime('%H:%M:%S %Z'), error_code))

            # Wait 1 second
            time.sleep(1)

        else:
            # Display error
            print("[ERROR]", "%s, MySQL Error %d: %s" % (time.strftime('%H:%M:%S %Z'), error_code, error_message))
            sys.exit("\nUnexpected MySQL error encountered")

    # Any other error bail out
    except:
        print(sys.exc_info()[1])
        sys.exit("\nUnexpected error encountered")
