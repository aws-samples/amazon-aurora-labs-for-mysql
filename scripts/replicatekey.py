"""
Amazon Aurora Labs for MySQL
Script to replicate multiregion keys from any region to current region. 
This script is run prior to adding a secondary global database region.

Dependencies:
none

License:
This sample code is made available under the MIT-0 license. See the LICENSE file.
"""

from logging import FATAL
import string
import argparse 
import boto3
from botocore.exceptions import ClientError
import sys

def validateregion(region):
# validates passed region name.
    try:
        regionfound = False

        for i in regionslist['Regions']:
            if (i['RegionName'] == region):
                regionfound = True
                break
            
        return regionfound
    
    except ClientError as e:
        print("[ERROR]",e)
    except Exception as e:
        print("[ERROR]", e)

def keyexists(kid):
    
    try:
    
        exists = False
        kmskeys = ckmsclient.list_keys()
        
        for key in kmskeys['Keys']:
            if (key['KeyId'] == kid):
                exists = True
        return exists
    
    except ClientError as e:
        print("[ERROR]",e)
    except Exception as e:
        print("[ERROR]", e)

def main():

    try:

        parser=argparse.ArgumentParser()
        parser.add_argument ("-r","--region", type=str, default='', help="List of regions separated by commas, where the stack will be deployed")

        # Passed current region 
        args = parser.parse_args()
        cregion = args.region

        # Get all possible regions

        global regionslist
        ec2client = boto3.client('ec2','us-east-1')
        regionslist = ec2client.describe_regions()

        # If no region was passed, try to detect using region for the current session. If no region was set for the session, exit.
        if not cregion:
            print ("Region was not passed, attempting to detect current region..")
            my_session = boto3.session.Session()
            my_region = my_session.region_name
            if not my_region:
                print ("Unable to detect current region. Likely reason is the client region was not set. Please rerun the script and provide current region using --region argument")
                sys.exit(0)
            else:
                if not validateregion(my_region):
                    print ("Please provide a valid region name in region list. For example: us-east-1. Incorrect region name", cregion, "was provided.")
                    sys.exit(1)
                else:
                    cregion=my_region


        # print ("Current region is",my_region)
        
        #kmsclient for current region. Used for replicating key in the current ket later.
        global ckmsclient
        ckmsclient = boto3.client('kms',region_name = cregion)

        print("Enumerating keys...")
        
        for regions in regionslist['Regions']:

            region = regions['RegionName']

            kmsclient = boto3.client('kms',region_name = region)
            kmskeys = kmsclient.list_keys()

            keycount = 0

            # Count keys in the region
            for key in kmskeys['Keys']:
                keycount += 1

            for key in kmskeys['Keys']:
                # print (key['KeyId'],region,cregion)
                kid=key['KeyId']
                keyresponse = kmsclient.describe_key(KeyId=kid)
                # Only replicate  multiregion primary key. If the key is in the same region, it cant be replicated.
                if (keyresponse['KeyMetadata']['MultiRegion'] and keyresponse['KeyMetadata']['MultiRegionConfiguration']['MultiRegionKeyType']=='PRIMARY' and keyresponse['KeyMetadata']['KeyState']=='Enabled'):
                    if (region==cregion):
                        print("Can't replicate a key in the same region. Skipping.")
                        if (keycount >0):
                            break
                        else:
                            sys.exit(2)
                    #If the key is already replicated in target region exit, else replicate key.
                    elif (keyexists(kid)):
                        print("Key already replicated in the region. skipping")
                        if (keycount >0):
                            break
                        else:
                            sys.exit(3)
                    else:
                        print ("Replicating key:",kid, "to current region:",cregion)
                        kmsclient.replicate_key(KeyId=kid,ReplicaRegion=cregion,Description="Multi region key replica for Global DB labs")
                        ckmsclient.create_alias(AliasName='alias/auroralab-mysql-db-key',TargetKeyId=kid)
                keycount -= 1

    
    except ClientError as e:
        print("[ERROR]",e)
    except Exception as e:
        print("[ERROR]", e)

if __name__ == "__main__":
    main()