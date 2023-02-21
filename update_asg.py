from flask import Flask, request
import boto3
import json
import datetime
import time
import os

app = Flask(__name__)

@app.route("/asg/", methods=['GET'])
def update_new_image():
    asg_name = request.args.get('asg_name', None)
    if not asg_name:
        return json.dumps({"result": "false","error_msg": "Please Input asg_name" })
    else: 
        session = boto3.Session(
            aws_access_key_id=os.getenv('ACCESS_KEY'),
            aws_secret_access_key=os.getenv('SECRET_KEY'),
            region_name=os.getenv('REGION_NAME'),
        )
        asg = session.client('autoscaling')
        ec2 = session.client('ec2')
        instance_ids = [] 

        # get asg filter by asg name
        asg_response = asg.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])

        # check exist asg
        if not asg_response['AutoScalingGroups']:
            return json.dumps({"result": "false","error_msg": "asg_name not exist" })
        
        timeStamp = time.time()
        timeStampString = datetime.datetime.fromtimestamp(timeStamp).strftime('%Y-%m-%d-%H-%M-%S')
        try: 
            # get InstanceId in asg
            for instance in asg_response['AutoScalingGroups']:
                for seri_instance in instance['Instances']:
                    instance_ids.append(seri_instance['InstanceId'])

            # create new AMI from 1 instance in asg
            newAMI_id = ec2.create_image(InstanceId=instance_ids[0], Name="New_AMI" + "_" + timeStampString)['ImageId']

        except Exception as Er_Create_Image:
            print(Er_Create_Image)
            return json.dumps({"result": "false","error_msg": "Error create Image" })
            
        try:   
            # create new LC
            newLC = asg_name + '_' + timeStampString
            asg.create_launch_configuration(
                InstanceId = instance_ids[0],
                LaunchConfigurationName=newLC,
                ImageId= newAMI_id
                )
            # update new LC for asg
            asg_response = asg.update_auto_scaling_group(AutoScalingGroupName = asg_name,LaunchConfigurationName = newLC)
            return json.dumps({"result": "true","nameLC": newLC })
        
        except Exception as Er_Create_LC:
            print(Er_Create_LC)
            return json.dumps({"result": "false","error_msg": "Error create LC " })
        
if __name__ == "__main__":
    app.run(port=5555)
