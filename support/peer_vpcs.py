"""
Amazon Aurora Labs for MySQL
Script to create a peering connection between two VPCs and configure the relevant routes and security group authorizations.

Dependencies:
none

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
"""

# Dependencies
import sys
import argparse
import time
import boto3
import random
import datetime
import json
import urllib3
from os import environ

# Define parser
parser = argparse.ArgumentParser()
parser.add_argument('-r', '--region_name', help="The local AWS region", required=False)
parser.add_argument('-p', '--peer_region', help="The remote AWS region")
parser.add_argument('-s', '--source_vpc', help="The VPC ID (source/requester) in the local AWS region")
parser.add_argument('-t', '--target_vpc', help="The VPC ID (target/accepter) in the remote region")
args = parser.parse_args()

# Track this lab for usage analytics, if user has explicitly or implicitly agreed
def track_analytics():
    http = urllib3.PoolManager()
    if ("AGREETRACKING" in environ and environ["AGREETRACKING"] == 'Yes'):
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
                'event_message': 'peer_vpcs.py',
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

# Create AWS session and clients
local_session = boto3.session.Session(region_name=args.region_name)
remote_session = boto3.session.Session(region_name=args.peer_region)
l_vpc = local_session.client('ec2')
r_vpc = remote_session.client('ec2')

try:
    # Get VPC details
    l_vpc_attrs = l_vpc.describe_vpcs(
        VpcIds=[args.source_vpc]
    )
    r_vpc_attrs = r_vpc.describe_vpcs(
        VpcIds=[args.target_vpc]
    )
    print("[INFO]", "Retrieved VPC configurations for: ", args.source_vpc, args.target_vpc)
    
    
    # Get route tables
    l_route_tables = l_vpc.describe_route_tables(
        Filters=[
        {
            'Name': 'vpc-id',
            'Values': [args.source_vpc]
        }
    ])
    r_route_tables = r_vpc.describe_route_tables(
        Filters=[
        {
            'Name': 'vpc-id',
            'Values': [args.target_vpc]
        }
    ])
    print("[INFO]", "Retrieved Route Tables for VPCs:", args.source_vpc, args.target_vpc)

    # Get DB security groups (tag value dbClusterSecGroup)
    l_db_sec_groups = l_vpc.describe_security_groups(
        Filters=[
        {
            'Name': 'vpc-id',
            'Values': [args.source_vpc]
        },
        {
            'Name': 'tag:aws:cloudformation:logical-id',
            'Values': ["dbClusterSecGroup"]
        }
    ])
    r_db_sec_groups = r_vpc.describe_security_groups(
        Filters=[
        {
            'Name': 'vpc-id',
            'Values': [args.target_vpc]
        },
        {
            'Name': 'tag:aws:cloudformation:logical-id',
            'Values': ["dbClusterSecGroup"]
        }
    ])

    # Create VPC peering connection
    result = l_vpc.create_vpc_peering_connection(
        PeerVpcId=args.target_vpc,
        VpcId=args.source_vpc,
        PeerRegion=args.peer_region
    )
    pcx = result["VpcPeeringConnection"]
    print("[INFO]", "Created new VPC Peering Connection:", pcx["VpcPeeringConnectionId"])
    print("[INFO]", "Waiting, connection state is:", pcx["Status"]["Code"])

    # Wait for the connection to reach pending acceptance state
    while pcx["Status"]["Code"] != "pending-acceptance":
        time.sleep(1)
        result = l_vpc.describe_vpc_peering_connections(
            VpcPeeringConnectionIds=[pcx["VpcPeeringConnectionId"]]
        )
        pcx = result["VpcPeeringConnections"][0]
        print("[INFO]", "Waiting, connection state is:", pcx["Status"]["Code"])

    # Accept the connection in the target region
    result = r_vpc.accept_vpc_peering_connection(
        VpcPeeringConnectionId=pcx["VpcPeeringConnectionId"]
    )
    print("[INFO]", "Accepted VPC Peering Connection in peer region:", pcx["VpcPeeringConnectionId"])

    # Wait until connection becomes available
    while pcx["Status"]["Code"] != "active":
        time.sleep(1)
        result = l_vpc.describe_vpc_peering_connections(
            VpcPeeringConnectionIds=[pcx["VpcPeeringConnectionId"]]
        )
        pcx = result["VpcPeeringConnections"][0]
        print("[INFO]", "Waiting, connection state is:", pcx["Status"]["Code"])

    # Update Route Tables with route to peer connection
    for rt in l_route_tables["RouteTables"]:
        for cidr in r_vpc_attrs["Vpcs"][0]["CidrBlockAssociationSet"]:
            result = l_vpc.create_route(
                DestinationCidrBlock=cidr["CidrBlock"],
                RouteTableId=rt["RouteTableId"],
                VpcPeeringConnectionId=pcx["VpcPeeringConnectionId"]
            )
            print("[INFO]", "Added peer route for:", cidr["CidrBlock"], "to:", rt["RouteTableId"])
    for rt in r_route_tables["RouteTables"]:
        for cidr in l_vpc_attrs["Vpcs"][0]["CidrBlockAssociationSet"]:
            result = r_vpc.create_route(
                DestinationCidrBlock=cidr["CidrBlock"],
                RouteTableId=rt["RouteTableId"],
                VpcPeeringConnectionId=pcx["VpcPeeringConnectionId"]
            )
            print("[INFO]", "Added peer route for:", cidr["CidrBlock"], "to:", rt["RouteTableId"])

    # Update ingress rules for Db security grous to allow peer region app security groups
    for db in l_db_sec_groups["SecurityGroups"]:
        ip_pairs = []
        for cidr in r_vpc_attrs["Vpcs"][0]["CidrBlockAssociationSet"]:
            ip_pairs.append({
                'CidrIp': cidr["CidrBlock"],
                'Description': "Peer region application source security group"
            })

        if len(ip_pairs):
            results = l_vpc.authorize_security_group_ingress(
                GroupId=db["GroupId"],
                IpPermissions=[
                    {
                        'FromPort': 3306,
                        'IpProtocol': "tcp",
                        'ToPort': 3306,
                        'IpRanges': ip_pairs
                    },
                ]
            )
            print("[INFO]", "Added security group authorizations to:", db["GroupId"])
    for db in r_db_sec_groups["SecurityGroups"]:
        ip_pairs = []
        for cidr in l_vpc_attrs["Vpcs"][0]["CidrBlockAssociationSet"]:
            ip_pairs.append({
                'CidrIp': cidr["CidrBlock"],
                'Description': "Peer region application source security group"
            })

        if len(ip_pairs):
            results = r_vpc.authorize_security_group_ingress(
                GroupId=db["GroupId"],
                IpPermissions=[
                    {
                        'FromPort': 3306,
                        'IpProtocol': "tcp",
                        'ToPort': 3306,
                        'IpRanges': ip_pairs
                    },
                ]
            )
            print("[INFO]", "Added security group authorizations to:", db["GroupId"])

# Trap keyboard interrupt, exit
except KeyboardInterrupt:
    sys.exit("\nStopped by the user")

# Generic errors
except Exception as e:
    # Errors in tracker interaction should not prevent operation of the function in critical path
    print("[ERROR]", e)