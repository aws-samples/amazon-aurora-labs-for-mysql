"""
Amazon Aurora Labs for MySQL
Read load generator using multiple threads

Changelog:
2019-06-14 - Initial release
2019-06-20 - Changed threading, added CPU heavy queries to boost load

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

# Define parser
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--endpoint', help="The database endpoint")
parser.add_argument('-p', '--password', help="The database user password")
parser.add_argument('-u', '--username', help="The database user name")
parser.add_argument('-d', '--database', help="The schema (database) to use")
parser.add_argument('-t', '--threads', help="The number of threads to use", type=int, default=64)
args = parser.parse_args()

# Global variables
query_count = 0
max_id = 2500000
query_iterations = 100
lock = threading.Lock()

# Query thread
def thread_func(endpoint, username, password, schema, max_id, iterations):
    # Specify that query_count is a global variable
    global query_count
    global lock

    # Loop Indefinitely
    while True:
        try:
            # Resolve the endpoint
            host = socket.gethostbyname(endpoint)

            # Connect to the reader endpoint
            conn = pymysql.connect(host=host, user=username, password=password, database=schema, autocommit=True)

            # Run multiple queries per connection
            for iter in range(iterations):
                # Generate a random number to use as the lookup value
                # we will arbitrarily switch between a few query types
                key_value = random.randrange(1, max_id)
                key_offset = random.randrange(1, 1000)
                query_type = random.randrange(0,5)

                # queries of multiple types
                if query_type == 0:
                    # Point query
                    sql_command = "SELECT SQL_NO_CACHE * FROM sbtest1 WHERE id= %d;" % key_value
                elif query_type == 1:
                    # Range query
                    sql_command = "SELECT SQL_NO_CACHE *, SHA2(c, 512), SQRT(k) FROM sbtest1 WHERE id BETWEEN %d AND %d ORDER BY id DESC LIMIT 10;" % (key_value, key_value + key_offset)
                elif query_type == 2:
                    # Aggregation
                    sql_command = "SELECT SQL_NO_CACHE k, COUNT(k), SQRT(SUM(k)), SQRT(AVG(k)) FROM sbtest1 WHERE id BETWEEN %d AND %d GROUP BY k ORDER BY k;" % (key_value, key_value + key_offset)
                elif query_type == 3:
                    # Point query with hashing
                    sql_command = "SELECT SQL_NO_CACHE id, SHA2(c, 512) AS token FROM sbtest1 WHERE id= %d;" % key_value
                elif query_type == 4:
                    # Point query with hashing
                    sql_command = "CALL minute_rollup(%d);" % (key_offset * 10)


                # run query
                with conn.cursor() as cursor:
                    cursor.execute(sql_command)
                    cursor.close()

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

    # Loop indefinitely
    while True:
        if initial != True:
            # Format an output string
            end_time = time.time()
            output = "Queries/sec: {0} (press Ctrl+C to quit)\r".format(int(query_count / (end_time-start_time)))
            start_time = end_time

            # Reset the executed query count
            with lock:
                query_count = 0

            # Write to STDOUT and flush
            sys.stdout.write(output)
            sys.stdout.flush()

            # Sleep this thread for 1 second
            time.sleep(5)

        # No longer initial pass
        initial = False

# Start progress thread
_thread.start_new_thread(progress_func, ())

# Start readers
for thread_id in range(args.threads):
        _thread.start_new_thread(thread_func, (args.endpoint, args.username, args.password, args.database, max_id, query_iterations))

# Loop indefinitely to prevent application exit
while 1:
        pass
