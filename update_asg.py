import boto3
import json
import datetime
import time
import sys

ACCESS_KEY = 'AKIAUXKJWWMEVXN63PPO'
SECRET_KEY = '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'
REGION_NAME = 'ap-southeast-1'

# asg_name = 'lab-asg'
# asg_name = str(input())
asg_name = str(sys.argv)

def update_new_image(asg_name):
    session = boto3.Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name=REGION_NAME,
    )

    # get autoscaling client
    asg = session.client('autoscaling')
    ec2 = session.client('ec2')
    instance_ids = [] 

    # get asg filter by asg name
    asg_response = asg.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])

    # check exist asg
    if not asg_response['AutoScalingGroups']:
        return json.dumps({"result": "false" })

    # get InstanceId in asg
    for i in asg_response['AutoScalingGroups']:
        for k in i['Instances']:
            instance_ids.append(k['InstanceId'])

    ec2_response = ec2.describe_instances(InstanceIds = instance_ids)   

    # create new AMI from 1 instance in asg
    timeStamp = time.time()
    timeStampString = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d-%H-%M-%S')
    
    newAMI_id = ec2.create_image(InstanceId=instance_ids[0], Name="New_AMI" + "_" + timeStampString)['ImageId']

    # create new LC
    newLC = asg_name + '_' + timeStampString

    asg.create_launch_configuration(
        InstanceId = instance_ids[0],
        LaunchConfigurationName=newLC,
        ImageId= newAMI_id
        )
    # update new LC for asg
    asg_response = asg.update_auto_scaling_group(AutoScalingGroupName = asg_name,LaunchConfigurationName = newLC)

    nameLC = print(json.dumps({"result": "true","nameLC": newLC }))

    return nameLC 

print(update_new_image(asg_name))






