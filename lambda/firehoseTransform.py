import base64
import json
import boto3
from database import Database
from datetime import datetime

# X-Ray SDK: instrument all SDKs
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all
patch_all()

# default encoding of bytes in the posted record
ENCODING = 'utf-8'

print('Loading function')
ddb = boto3.resource('dynamodb')
database = Database(ddb)

def lambda_handler(event, context):
    source_records = []
    query_devices = set()

    print("Received batch of {} records".format(len(event['records'])))

    for record in event['records']:
        payload = base64.b64decode(record['data']).decode(ENCODING)

        event = json.loads(payload)

        source_records.append({
            'recordId' : record['recordId'],
            'event' : dict(event) # copy of event
        })

        query_devices.add(event['device_id'])

    device_details = database.getDeviceDetails(query_devices)

    output = []
    successes = 0

    for record in source_records:
        event = record['event']
        device_id = event['device_id']

        if(device_id in device_details):
            # we have device details
            details = device_details[device_id]

            # copy existing event
            trans_event = dict(event)

            # convert timestamp to human readable ISO8601 string
            trans_event['timestamp'] = datetime.utcfromtimestamp(event['timestamp']/1000).isoformat()

            # enrich event with device details
            trans_event['manufacturer'] = details['manufacturer']
            trans_event['model'] = details['model']

            trans_payload = json.dumps(trans_event) + "\n"

            output_record = {
                'recordId': record['recordId'],
                'result': 'Ok',
                'data': base64.b64encode(trans_payload.encode(ENCODING)).decode(ENCODING)
            }
            successes += 1
            output.append(output_record)
        else:
            # we couldn't get device details: flag that as an error to firehose
            output_record = {
                'recordId': record['recordId'],
                'result': 'ProcessingFailed',
                'data': None
            }
            output.append(output_record)

    print('Successfully processed {} out of {} records.'.format(successes, len(source_records)))
    return {'records': output}
