"""
Amazon Aurora Labs for MySQL
Script to demonstrate Aurora MySQL Serverless v2 scaling.

Dependencies:
none

Initial release : 5/20/2022
Written By      : ausamant
Bug fix         : 5/26/2022 - ausamant - fixed thread crashing when posting cw metrics 

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
"""

import sys
import argparse
import time
import datetime
import threading
import socket
import pymysql
from pymysql.constants import CLIENT
import boto3
from botocore.exceptions import ClientError
from os import environ
import urllib3
import json



parser = argparse.ArgumentParser()
required = parser.add_argument_group('Required Arguments')
required.add_argument('-e', '--endpoint', help="The database endpoint")
required.add_argument('-p', '--password', help="The database user password")
required.add_argument('-u', '--username', help="The database user name")
required.add_argument('-d', '--database', help="The schema (database) to use")

args = parser.parse_args()

# define queries
query_search_catalog1 = "SELECT sum(stock) FROM products WHERE category = \"shoes\" AND product_id < 50000;SELECT sum(stock) FROM products WHERE category = \"lipstick\" AND product_id < 50000;"
query_place_order = "INSERT INTO orders (product_name, quantity) values (\"comfy\", 1);SELECT COUNT(*) FROM orders;"
query_update_order1 = "SELECT count(p.product_name), sum(p.stock - o.quantity) FROM products p INNER JOIN orders o ON o.product_name = p.product_name;"
query_runonce_create ="CREATE TABLE IF NOT EXISTS products (product_id INT NOT NULL AUTO_INCREMENT, product_name VARCHAR(100), category VARCHAR(100), stock INT, PRIMARY KEY (product_id)); CREATE TABLE IF NOT EXISTS orders (customer_id INT NOT NULL AUTO_INCREMENT, product_name VARCHAR(100), quantity INT, PRIMARY KEY (customer_id));"
query_runonce_cleanup ="TRUNCATE TABLE products;TRUNCATE TABLE orders;"
query_runonce_insert ="INSERT INTO products (category, product_name, stock) VALUES (\"shoes\", \"comfy\", 100), (\"shoes\", \"hi-top\", 100), (\"shoes\", \"clown\", 100); INSERT INTO products (category, product_name, stock) VALUES (\"lipstick\", \"high-gloss\", 100), (\"lipstick\", \"moist\", 100), (\"lipstick\", \"blush\", 100);"


# Condition to quit. Initially set to false
exitflag = False

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
                'event_message': 'serverlessv2_demo.py',
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



def publish_metric():
# Function to add custom Cloudwatch metric data point
    try:

        #hack to make cwclient thread safe. Without this, client creation throws exceptions. A lock might work too, I haven't tried it.
        cond = True
        while cond:
            try:
                cwclient = boto3.client('cloudwatch')
                cond = False
            except:
                cond = True
        
        cwresponse = cwclient.put_metric_data(
        Namespace='MyFlashSale/Orders',
        MetricData=[
            {
                'MetricName': 'Orders',
                'Dimensions': [
                    {
                        'Name': 'OfferType',
                        'Value': 'FlashSale'
                    },
                ],
                'Value': 1.0,
                'Unit': 'Count',
                'StorageResolution': 1
            }
            ])

        
    except ClientError as e:
        print(e)
        raise

def exec_sql(querytext,conn):
# Function to execute passed query text and return results
    try:

        with conn.cursor() as cursor:
            cursor.execute(querytext)
            result = cursor.fetchall()
            cursor.close()
        
        return result

    except ClientError as e:
        print(e)
        raise

def runonce (endpoint, username, password,schema):
    try:
        host = socket.gethostbyname(endpoint)

        # Connect to the db endpoint
        conn = pymysql.connect(host=host, user=username, password=password, database=schema, autocommit=True,client_flag= CLIENT.MULTI_STATEMENTS)
        
        exec_sql(query_runonce_create,conn)
        exec_sql(query_runonce_cleanup,conn)

        i=1
        for i in range (1,8,1):
            exec_sql(query_runonce_insert,conn)
        
        # Close the connection
        conn.close()

    except ClientError as e:
        print(e)
        raise

def worker_thread(endpoint, username, password, schema):
    # Using global variables
    global stats_latency
    global lock
    global total_thread_count
    
    with lock:
        total_thread_count=total_thread_count+1

    # Try/catch block
    try:
        # Resolve the endpoint
        host = socket.gethostbyname(endpoint)

        # Connect to the db endpoint
        conn = pymysql.connect(host=host, user=username, password=password, database=schema, autocommit=True,client_flag= CLIENT.MULTI_STATEMENTS)
      
        j=0
        while  j<=50:
            # Execute query
            
            # publish_metric()
            # time.sleep(1)
            
            exec_sql(query_search_catalog1,conn)
            exec_sql(query_place_order,conn)
            exec_sql(query_update_order1,conn)
            
            #Sleep for a second so cloudwatch can catch up
            time.sleep(0.5)
            publish_metric()
            j+=1

        # Close the connection
        conn.close()
        

        with lock:
            total_thread_count=total_thread_count-1
            
        

    # Trap keyboard interrupt, exit
    except KeyboardInterrupt:
        # Signal we need to exit
        with lock:
            exitflag = True

        # Send some feedback
        print("Exiting, please wait...")

    # Trap generic errors
    except ClientError as e:
        print(e)
        raise

# def report_progress(thread_number,max_iteration):
def report_progress(endpoint, username, password):
    
    global exitflag
    global total_thread_count
    
    host = socket.gethostbyname(endpoint)
    try:
        # Start timing
        start_time = time.time()
        mysql_stats ="select count(host), round (@@innodb_buffer_pool_size/1024/1024/1024,2),"
        mysql_stats = mysql_stats+"COUNT FROM Information_schema.innodb_metrics, Information_schema.processlist"
        mysql_stats = mysql_stats+" WHERE name=\"trx_rseg_history_len\""

        print ("""
  +-------------------------------+-------------------------------+-------------------------------+-------------------------------+
  |           Current Connections | Innodb Buffer Pool Size (GiB) | InnoDB History List Length    | Total Threads Started         |
  +-------------------------------+-------------------------------+-------------------------------+-------------------------------+""")
        
        sys.stdout.flush()

        # Loop indefinitely
        while True:
            # Exit loop if we got a signal to do so
            if exitflag:
                break

            # Connect to mysql and execute MySQL stats query until script stops    
            conn = pymysql.connect(host=host, user=username, password=password, database='mysql', autocommit=True,client_flag= CLIENT.MULTI_STATEMENTS)
            result = exec_sql(mysql_stats,conn)
            
            # Assemble final result
            result1="  |"
            for i in range(0, len(result), 1):
                for row in result[i]:
                    spaces=(31-len(str(row)))*" "
                    result1= result1+spaces+str(row)+"|"
            
            # total_thread_count variable needs to be thread safe
            with lock:
                spaces = (31-len(str(total_thread_count)))*" "
                result1= result1+spaces+str(total_thread_count)+"|"

            sys.stdout.flush()
            print(result1,"""
  +-------------------------------+-------------------------------+-------------------------------+-------------------------------+""", end='\r')
            sys.stdout.flush()

            # Sleep this thread for 5 second
            time.sleep(5)

    # Trap keyboard interrupt, exit
    except KeyboardInterrupt:
        # Signal we need to exit
        with lock:
            exitflag = True

        # Send some feedback
        print("Exiting, please wait...")

    # Trap generic errors
    except ClientError as e:
        print(e)
        raise


def main():

    global thread_count
    global total_thread_count
    global lock

    # Initialize thread lock
    lock = threading.Lock()

    try:
        
        # invoke analytics
        track_analytics()
        
        # Schema creation or cleanup
        runonce (args.endpoint, args.username, args.password, args.database)

        # Start the progress reporting  thread to display stats of the screen,
        thread_count = 0
        total_thread_count = 0
        y = threading.Thread(target=report_progress, args=(args.endpoint, args.username, args.password))
        y.start()

        # Start the worker thread to scale up ACUs
        for external_tc in range (1,8,1):
            if exitflag:
                    break
            thread_count = 1
            while thread_count<external_tc*10:
                
                # Exit loop if we got a signal to do so
                if exitflag:
                    break
                
                x = threading.Thread(target=worker_thread, args=(args.endpoint, args.username, args.password, args.database) )
                x.start()
                thread_count+=1
                time.sleep(0.5)
            if exitflag:
                    break
            time.sleep(15)

        # thread_count = 100
        # # Start the worker thread to scale down ACUs
        # for external_tc in range (10,-2,-2):
        #     if exitflag:
        #             break
        #     thread_count = external_tc*10
        #     while thread_count>=external_tc*10:
                
        #         # Exit loop if we got a signal to do so
        #         if exitflag:
        #             break
                
        #         x = threading.Thread(target=worker_thread, args=(args.endpoint, args.username, args.password, args.database) )
        #         x.start()
        #         thread_count-=1
        #         time.sleep(0.5)
        #     time.sleep(5)



    except ClientError as e:
        print(e)
        raise

if __name__ == "__main__":
    main()