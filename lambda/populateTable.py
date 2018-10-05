import boto3
import json
import requests
import os
import random

# Number of devices
DEVICES = 10000

# Number of manufacturers
MANUFACTURERS = 20

# Number of models
MODELS = 20

TABLE_NAME = os.environ['TABLE_NAME']

ddb = boto3.resource('dynamodb')

table = ddb.Table(TABLE_NAME)

def populate():
    for i in range(0, DEVICES):
        item = {
                'device_id' : 'device{num:04d}'.format(num=i),
                'manufacturer' : 'Manufacturer {num:02d}'.format(num = random.randrange(MANUFACTURERS)),
                'model' : 'Model {num:02d}'.format(num = random.randrange(MODELS))
                }

        if(i % 100 == 0):
            print('Adding ' + json.dumps(item))
        table.put_item(Item = item)

def respond_cloudformation(event, status, data=None):
    responseBody = {
            'Status': status,
            'Reason': 'See the details in CloudWatch Log Stream',
            'PhysicalResourceId': 'Custom Lambda Function',
            'StackId': event['StackId'],
            'RequestId': event['RequestId'],
            'LogicalResourceId': event['LogicalResourceId'],
            'Data': data
            }

    print('Response = ' + json.dumps(responseBody))
    requests.put(event['ResponseURL'], data=json.dumps(responseBody))

def lambda_handler(event, context):
    print(event)
    reqtype = event['RequestType']

    if(reqtype == 'Create'):
        populate()

    respond_cloudformation(event, 'SUCCESS')
