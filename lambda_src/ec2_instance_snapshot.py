# -*- coding: utf-8 -*-
"""
.. module: ec2_instance_snapshot.py
    :Create EC2 Volume Snapshot: Helpful for remediation 
    :platform: AWS
    :copyright: (c) 2020 Mystique.,
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mystique
.. contactauthor:: miztiik@github issues
"""

import boto3
import os
import logging

# Initialize Logger
logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s", datefmt="%H:%M:%S"
)
logger.setLevel(os.getenv('log_level', logging.INFO))

def create_instance_snapshot( inst_id ):
    client = boto3.client('ec2')
    response = client.describe_instances(
        InstanceIds=[
            inst_id
        ]
    )
    volumeID = response['Reservations'][0]['Instances'][0]['BlockDeviceMappings'][0]['Ebs']['VolumeId']
    logger.info(f"volumeID: {volumeID}")
    SnapShotDetails = client.create_snapshot(
        Description='Isolated Instance',
        VolumeId=volumeID
    )
    # TODO Dump Response into S3 - response
    # TODO Dump Response details into Snapshot - SnapShotDetails['SnapshotId']

    logger.info(f"SnapShotDetails: {SnapShotDetails['SnapshotId']}")

    tagresponse = client.create_tags(
        Resources=[
            SnapShotDetails['SnapshotId'],
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': 'QUARANTINED-INSTANCE-SNAPSHOT'
            },
            {
                'Key': 'InstanceId',
                'Value': f"{inst_id}"
            },
            {
                'Key': 'Miztiik-InfoSec-Corp',
                'Value': 'https://github.com/miztiik/security-incident-response-instance-isolation'
            },
        ]
    )

    waiter = client.get_waiter('snapshot_completed')
    waiter.wait(
        SnapshotIds=[
            SnapShotDetails['SnapshotId'],
        ]
    )

    return SnapShotDetails['SnapshotId']

def lambda_handler(event, context):
    logger.info(f"Event:{event}")
    inst_id = event.get('instanceId')
    if not inst_id:
        inst_id ="i-08e8f2947d47af658"
    resp = create_instance_snapshot( inst_id )
    return resp

if __name__ == '__main__':
    lambda_handler({}, {})