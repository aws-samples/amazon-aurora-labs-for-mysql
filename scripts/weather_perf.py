"""
Amazon Aurora Labs for MySQL
load generator using multiple threads. The script will randomize a set of query patterns,
including point query, range query, aggregation and expensive stored procedure.

Dependencies:
none

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
"""

# Dependencies
import sys
import argparse
import time
import threading
import _thread
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
parser.add_argument('-d', '--database', help="The schema (database) to use", required=True)
parser.add_argument('-t', '--threads', help="The number of threads to use", type=int, default=5)
args = parser.parse_args()

# Global variables
query_count = 0
temp_id = 50
max_id= 2500000
query_iterations = 50
lock = threading.Lock()


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
                'event_message': 'weather_perf.py',
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

# Query thread

stations=["YUMA","SANDBERG","MURDA","MEACHAM","EAGLE MTN"]
types=["Weak Cold","Strong Hot","Weak Hot","Strong Cold"]
station_id=["USC00103882","USC00046699"]
def thread_func(endpoint, username, password, schema, max_id, iterations):
    # Specify that query_count is a global variable
    global query_count
    global lock
    count = 0
    try:
    # Resolve the endpoint
        host = socket.gethostbyname(endpoint)
        # Connect to the reader endpoint
        conn = pymysql.connect(host=host, user=username, password=password, database=schema, autocommit=True)
        # Run multiple queries per connection
        for iter in range(iterations):
            # Generate a random number to use as the lookup value
            # we will arbitrarily switch between a few query types
            temp_value = random.randrange(10, temp_id)
            key_value = random.randrange(1, max_id)
            key_offset = random.randrange(1, 1000)
            query_type = random.randrange(0,9)
            station_name: str=random.choice(stations)
            stationid: str=random.choice(station_id)
            type=random.choice(types)
            # queries of multiple types
            if query_type == 0:
                # Point query
                sql_command = "SELECT SQL_NO_CACHE id, SHA2(c, 512) AS token FROM sbtest1 WHERE id= %d;" % (key_value)
            elif query_type == 1:
                # Range query
                sql_command = "SELECT sql_no_cache count(id) FROM weather WHERE station_name = '%s' and type = '%s';"  % (station_name,type)
            elif query_type == 2:
                # stored procedure
                sql_command = "CALL insert_temp;"
            elif query_type == 3:
                    # Point query with hashing
                sql_command = "CALL minute_rollup(%d);" % (key_offset * 10)
            elif query_type == 4:
                # Point query with hashing
                sql_command = "UPDATE mylab.weather SET max_temp = %d where id='%s';" %(temp_value,stationid)
            elif query_type == 5:
                    # Point query
                sql_command = "SELECT SQL_NO_CACHE * FROM sbtest1 WHERE id= %d;" % (key_value)
            elif query_type == 6:
                    # Range query
                sql_command = "SELECT SQL_NO_CACHE *, SHA2(c, 512), SQRT(k) FROM sbtest1 WHERE id BETWEEN %d AND %d ORDER BY id DESC LIMIT 10;" % (key_value, key_value + key_offset)
            elif query_type == 7:
                # Aggregation
                sql_command = "SELECT SQL_NO_CACHE k, COUNT(k), SQRT(SUM(k)), SQRT(AVG(k)) FROM sbtest1 WHERE id BETWEEN %d AND %d GROUP BY k ORDER BY k;" % (key_value, key_value + key_offset)
            elif query_type == 8:
                # Point query with hashing
                sql_command = "SELECT sql_no_cache max_temp,min_temp,station_name FROM weather WHERE max_temp > %d and id = '%s' ORDER BY max_temp DESC;" % (temp_value,stationid)
                # run query
            with conn.cursor() as cursor:
                print("executing %s... .." %sql_command)
                cursor.execute(sql_command)
                cursor.close()
                # run query
                # Increment the executed query count
            with lock:
                query_count += 1
        # Close the connection
        conn.close()
    except:
        # Display any exception information
        print(sys.exc_info()[1])


# Progress thread
def progress_func():
    # Specify that query_count is a global variable
    global query_count
    global lock

    # Start timing
    start_time = time.time()
    initial = True
    count=0

    # Loop indefinitely
    while True:
        if initial != True:
            # Format an output string
            end_time = time.time()
            output = "Queries/sec: {0} (press Ctrl+C when it hit Queries/sec: 0 after few mins )\r".format(int(query_count / (end_time-start_time)))
            start_time = end_time

            # Reset the executed query count
            with lock:
                query_count = 0

            # Write to STDOUT and flush
            sys.stdout.write(output)
            sys.stdout.flush()

            # Sleep this thread for .5 second
            time.sleep(.5)

        # No longer initial pass
        initial = False


# Invoke tracking function
track_analytics()

# Start progress thread
_thread.start_new_thread(progress_func, ())

# Start readers
for thread_id in range(args.threads):
    _thread.start_new_thread(thread_func, (args.endpoint, args.username, args.password, args.database, max_id, query_iterations))

# Loop indefinitely to prevent application exit
while 1:
    pass
