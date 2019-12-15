# -*- coding: utf-8 -*-
"""
.. module: ec2_instance_quarantine
    :Attaches: the instance a SG with no rules so it can't communicate with the outside world
    :platform: AWS
    :copyright: (c) 2020 Mystique.,
    :license: Apache, see LICENSE for more details.
.. moduleauthor:: Mystique
.. contactauthor:: miztiik@github issues
"""

import boto3
import os
from botocore.exceptions import ClientError
import logging

# Initialize Logger
logger = logging.getLogger()
logging.basicConfig(
    format="[%(asctime)s] %(levelname)s [%(module)s.%(funcName)s:%(lineno)d] %(message)s", datefmt="%H:%M:%S"
)
logger.setLevel(os.getenv('log_level', logging.INFO))


def set_global_vars():
    global_vars = {'status': False}
    global_vars['Owner']                    = "Mystique"
    global_vars['Environment']              = "Prod"
    global_vars['region_name']              = "us-east-1"
    global_vars['tag_name']                 = "ec2_instance_quarantine"
    global_vars['status']                   = True
    return global_vars

def get_qurantine_sg_id(inst_id):
    ec2_resource = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')

    q_sg_name="infosec-quarantine"

    inst_attr = ec2_client.describe_instances( InstanceIds=[inst_id] )['Reservations'][0]['Instances'][0]
    if inst_attr:
        inst_vpc_id = inst_attr.get('VpcId')

    # Check or create the Quarantine SG
    try:    
        result = ec2_client.describe_security_groups(
            Filters=[
                    {
                        'Name': 'group-name',
                        'Values': [q_sg_name]
                    },
                    {
                        'Name': 'vpc-id',
                        'Values': [inst_vpc_id]
                    }
                ]
            )
        if result['SecurityGroups']: 
            quarantine_sg_id = result['SecurityGroups'][0]['GroupId']
            logger.info(f"Found Existing quarantine sg_id: {quarantine_sg_id}")

        else:
            result = ec2_client.create_security_group(
                    Description='Quarantine Security Group. No ingress or egress rules should be attached.',
                    GroupName=q_sg_name,
                    VpcId=inst_vpc_id 
                    )

            # When a SG is created, AWS automatically adds in an outbound rule we need to delete
            security_group = ec2_resource.SecurityGroup(result['GroupId'])
            delete_outbound_result = security_group.revoke_egress(
                GroupId=result['GroupId'],
                IpPermissions=[{'IpProtocol':'-1','IpRanges': [{'CidrIp':'0.0.0.0/0'}]}]
                )
            tag = security_group.create_tags(Tags=[
                {'Key': 'Name','Value': "QUARANTINE-SG"},
                {'Key': 'Miztiik-InfoSec-Corp','Value': "https://github.com/miztiik/security-incident-response-instance-isolation"}
                ]
            )
            logger.info(f"New quarantine Security Group Created. sg_id: {result['GroupId']}")
            quarantine_sg_id = result['GroupId']
        
    except ClientError as e:
        logger.info(f"Unable to find or create quarantine security group")
        logger.info(f"ERROR: {str(e)}")

    return quarantine_sg_id

def quarantine_ec2_instance(inst_id, quarantine_sg_id):

    resp = {'status': False, 'instances_quarantined': [] }

    ec2_resource = boto3.resource('ec2')

    # Attach the instance to only the quarantine SG
    try:
        result = ec2_resource.Instance(inst_id).modify_attribute(Groups=[quarantine_sg_id])  
        responseCode = result['ResponseMetadata']['HTTPStatusCode']
        if responseCode >= 400:
            logger.info(f"Unable to modify instance security group")
            logger.info(f"ERROR:{str(result)}")
        else:
            logger.info(f"Instance:{inst_id} quarantined with sg:{quarantine_sg_id}")
            resp['status'] = True
            resp['instances_quarantined'].append(inst_id )

    except ClientError as e:
        logger.info(f"Unable to modify instance security group")
        logger.info(f"ERROR: {str(e)}")

    return resp

def lambda_handler(event, context):
    inst_id = event.get('instanceID')
    if not inst_id:
        inst_id="i-08e8f2947d47af658"
    quarantine_sg_id = get_qurantine_sg_id(inst_id)
    resp = quarantine_ec2_instance(inst_id, quarantine_sg_id)
    return resp

if __name__ == '__main__':
    lambda_handler(None, None)