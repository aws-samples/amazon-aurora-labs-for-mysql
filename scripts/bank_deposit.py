"""
Amazon Aurora Labs for MySQL
This scripts will allow you to deposit money into an account to observe write forwarding consistency effects

Changelog:
2020-11-16 - Initial release

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

# Define parser
parser = argparse.ArgumentParser()
parser.add_argument('-e', '--endpoint', help="The database endpoint", required=True)
parser.add_argument('-p', '--password', help="The database user password", required=True)
parser.add_argument('-u', '--username', help="The database user name", required=True)
parser.add_argument('-c', '--consistency', help="The consistency mode to use for Aurora Global Database write forwarding", choices=['EVENTUAL', 'SESSION', 'GLOBAL'], required=True)
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
                'event_message': 'bank_deposit.py',
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


# Perform a database query
def query_db(conn, query, first_row=False):
    results = []
    with conn.cursor() as cur:
        cur.execute(query)
        for r in cur.fetchall():
            row = []
            for i, value in enumerate(r):
                row.append(value)

            results.append(row)
        
        cur.close()
    
    return (results[0] if results else None) if first_row else results

# View banking summary
def show_summary(accounts, transactions, elapsed):
    # Print summary
    print("Account Summary:")
    summary = PrettyTable()
    summary.field_names = ["Account Number", "Balance ($)", "Type", "Status"]
    for r in accounts:
        summary.add_row(r)
    print(summary)

    # Print latest transactions
    print("\nLatest Transactions:")
    latest = PrettyTable()
    latest.field_names = ["Date and Time", "Account Number", "Amount ($)", "Type", "Description"]
    for r in transactions:
        latest.add_row(r)
    print(latest)

    # Print latency
    print("\nQueries took: %.4f seconds" % elapsed)

# Process a deposit
def make_deposit(conn):
    # ask for deposit
    while True:
        try:
            print("Make a deposit to your checking account.")
            deposit_amount=input("Enter deposit amount ($): ")
            deposit_amount = int(deposit_amount)
            if isinstance(deposit_amount, int) is False:
                raise ValueError("Please deposit full dollar amounts!")
        except ValueError:
            print("Please deposit full dollar amounts!")
            continue
        else:
            break

    # deposit the amount
    conn.begin()
    with conn.cursor() as cursor:
        cursor.execute("INSERT INTO `transactions` (`account_number`, `trx_medium`, `trx_type`, `trx_amount`) VALUES ('012948503534', 'Cash', 'Deposit', %d);" % deposit_amount)
        cursor.execute("UPDATE `accounts` SET `total_balance` = `total_balance` + %d WHERE `account_number` = '012948503534';" % deposit_amount)
        cursor.close()
    conn.commit()


# Invoke tracking function
track_analytics()

try:
    # Resolve the endpoint
    host = socket.gethostbyname(args.endpoint)

    # Connect to the desired endpoint
    conn = pymysql.connect(host=args.endpoint, user=args.username, password=args.password, database='mybank', autocommit=True, connect_timeout=10)

    # Set consistency
    sql_cmd = "SET aurora_replica_read_consistency = '%s';" % args.consistency
    with conn.cursor() as cursor:
        cursor.execute(sql_cmd)
        cursor.close()

    # Retrieve consistency
    consistency = query_db(conn, "SELECT @@aurora_replica_read_consistency;", first_row=True)[0]

    # Loop Indefinitely
    while True:
        # Clear screen, print welcome and consistency mode
        system("clear")
        print("=================================")
        print("Welcome to MyBank Deposit Portal!")
        print("=================================\n")
        print("Selected read consistency mode is: %s\n\n" % consistency)

        start_time=time.time()
        accounts = query_db(conn, "SELECT account_number, total_balance, account_type, account_status FROM accounts WHERE customer_id = 1 AND account_status IN ('Active', 'Delinquent') ORDER BY account_type ASC;")
        transactions = query_db(conn, "SELECT trx_tstamp, t.account_number, trx_amount, trx_type, trx_medium FROM transactions t INNER JOIN accounts a ON a.account_number = t.account_number WHERE a.customer_id = 1 ORDER BY trx_tstamp DESC LIMIT 5;")
        end_time=time.time()

        # Display account summary
        show_summary(accounts, transactions, end_time - start_time)

        # Prompt for next step
        next_step = input("\nType '[D]eposit' to add money, '[R]efresh' to refresh dashboard, '[Q]uit' to exit + <Enter>: ")
            
        # Exit the application
        if (next_step.lower() == "quit" or next_step.lower() == "q"):
            break

        # Or deposit some money
        elif (next_step.lower() == "deposit" or next_step.lower() == "d"):
            make_deposit(conn)


# Trap keyboard interrupt, exit
except KeyboardInterrupt:
    sys.exit("\nStopped by the user")

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
    sys.exit("\nUnexpected error encountered")
