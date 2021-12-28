import datetime
import json
import os
import uuid
import boto3
import ast
import time 

KMS_KEY_ID = os.environ['KMS_KEY_ID']
ssm = boto3.client('ssm')

def handler(event, context):
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    # setting source path 
    source_path=ssm.get_parameter(Name='/AIMLtoy/Workloads/Misc/SourcePath')['Parameter']['Value'])
    # set destination path 
    destination_path=ssm.get_parameter(Name='/AIMLtoy/Workloads/Misc/DestinationPath')['Parameter']['Value'])
    # number of days to set up observational window.
    days_ow = ssm.get_parameter(Name='/AIMLtoy/Workloads/Misc/DaysOW')['Parameter']['Value']) 
    
    for country in active_countries:
        data = {
          "InputData": {
            "vRun": "OK"
          },
          "CreditRiskFE": {
                  "Arguments": {"--today": str(today),
                                "--kms_key_id": KMS_KEY_ID,
                                "--source_path":source_path
                  }
              },
          "CRtrainingJob": {
                  "Arguments": {"--today": str(today),
                                "--source_path":destination_path,
                                "--kms_key_id": KMS_KEY_ID,
                                "--days_observational_windows": days_ow
                  }
              },
          "Backtesting": {
                "Arguments": {"--today": str(today),
                              "--source_path":destination_path,
                              "--days_observational_windows": days_ow
                } 
            },
        }
        client = boto3.client('stepfunctions')
        response = client.start_execution(
            stateMachineArn=STATE_MACHINE,
            name=str(uuid.uuid4()),
            input=json.dumps(data),
            traceHeader=str(uuid.uuid4())
        )
        print(json.dumps(data))
        time.sleep(2)
    return True

