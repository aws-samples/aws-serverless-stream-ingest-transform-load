import time
import os
import random
from cache import Cache

# cache timeout in seconds
CACHE_TIMEOUT = 15*60 # 15 minutes

# DDB Table name
TABLE_NAME = os.environ['TABLE_NAME']

# DDB Batch Size Max
DDB_BATCH_SIZE = 100

# Exponential Backoff Retry with "Full Jitter" from:
# https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
BASE = 2 # seconds
CAP = 10 # seconds
MAX_ATTEMPTS = 5 # retry 5 times max
def expBackoffFullJitter(attempt):
    return random.uniform(0, min(CAP, pow(2, attempt)*BASE))

class Database:
    def __init__(self, ddb):
        self.ddb = ddb
        self.cache = Cache(CACHE_TIMEOUT)


    def queryDDB(self, device_id_list, response):
        attempt = 0
        # loop with delay until MAX_ATTEMPTS or we have no more unprocessed records
        while(attempt < MAX_ATTEMPTS):
            unprocessed = []
            self.batchQueryDDB(device_id_list, response, unprocessed)
            if(len(unprocessed) == 0):
                break
            else:
                delay = expBackoffFullJitter(attempt)
                time.sleep(delay)
                attempt += 1
                device_id_list = unprocessed

    def batchQueryDDB(self, device_id_list, response, unprocessed):
        print("Querying details for {} devices from DynamoDB".format(len(device_id_list)))

        for i in range(0, len(device_id_list), DDB_BATCH_SIZE):
            keys = []
            j = i
            while j < len(device_id_list) and j < (i + DDB_BATCH_SIZE):
                device_id = device_id_list[j]
                j += 1
                keys.append({
                    'device_id' : device_id
                })


            result = self.ddb.batch_get_item(
                RequestItems = {
                    TABLE_NAME : {
                        'Keys' : keys
                    }
                }
            )

            for r in result['Responses'][TABLE_NAME]:
                device_id = r['device_id']

                device_details = {
                    'manufacturer' : r['manufacturer'],
                    'model' : r['model']
                }

                self.cache.put(device_id, device_details)
                response[device_id] = device_details

            unproc_count = 0
            if TABLE_NAME in result['UnprocessedKeys']:
                unproc = result['UnprocessedKeys'][TABLE_NAME]["Keys"]
                unproc_count = len(unproc)
                for u in unproc:
                    unprocessed.append(u['device_id'])

            print("DDB Query: {} results, {} unprocessed out of {} keys".format(
                len(result['Responses'][TABLE_NAME]),
                unproc_count,
                len(keys)))

    def getDeviceDetails(self, device_id_set):
        response = {}
        query_device_ids = []

        for device_id in device_id_set:
            device_details = self.cache.get(device_id)
            if(device_details is None):
                query_device_ids.append(device_id)
            else:
                response[device_id] = device_details

        if len(query_device_ids) > 0:
            self.queryDDB(query_device_ids, response)
        return response
