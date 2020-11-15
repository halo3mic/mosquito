import time
import csv
import os
import json
from pprint import pprint

from src.config import *
from src.dev_main import ws_receiver
from src.opportunities import EmptySet


def process_input_w_log(msg_org, queue):
    receiving_time = time.time()
    global starting_block, es
    os.system("clear")
    opp = es
    # for _ in range(opps.qsize()):
    STORAGE = queue.get()
    opp.STORAGE = STORAGE
    print(opp)
    msg = json.loads(msg_org)["params"]["result"]
    block_number = int(msg["number"].lstrip("0x"), 16)
    timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
    t0 = time.time()
    opportunity_detected = check_plans(opp, block_number, timestamp)
    t1 = time.time()
    processing_time_opp = t1 - t0
    processing_time_all = t1 - receiving_time

    queue.put(opp.STORAGE)
    results = {"blockNumber": block_number, 
               "blockTimestamp": timestamp, 
               "receivingTime": int(receiving_time), 
               "oppProcessingTime": processing_time_opp, 
               "wholeProcessingTime": processing_time_all,
               "opportunityFound": opportunity_detected, 
               "providerName": provider, 
               "opportunity": str(opp)
               }
    log_results(results)


    blocks_processed = block_number - starting_block
    print("PROVIDER: ", provider)
    print("BLOCK NUMBER: ", block_number)
    print("BLOCKS PROCESSED: ", blocks_processed)


def check_plans(opp, block_number, block_timestamp):
    payload = opp(block_number, block_timestamp)
    return bool(payload)


def log_results(results):
    with open(result_log_path, "a") as result_log:
        writer = csv.DictWriter(result_log, fieldnames=results.keys())
        # writer.writeheader()
        writer.writerow(results)


def main(provider_name):
    global w3, es, starting_block, provider, result_log_path
    # Settings
    result_log_path = "./logs/node_latency.csv"
    error_log_path = "./logs/errors.txt"
    wallet_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
    html_provider = NODE_INFO[provider_name]["html_path"]
    ws_provider = NODE_INFO[provider_name]["ws_path"]
    data_request = NODE_INFO[provider_name]["ws_blocks_request"]
    w3 = Web3(Web3.HTTPProvider(html_provider))

    # Globals vars
    es = EmptySet(w3, wallet_address)
    starting_block = w3.eth.blockNumber
    provider = provider_name

    last_error = None
    while 1:
        try:
            print("Logger started ...")
            ws_receiver(ws_provider, data_request, process_input_w_log)
        except Exception as e:
            raise e



if __name__ == "__main__":
    # provider = input()
    provider = "localNode"
    main(provider)
    # fieldnames = ["blockNumber", "blockTimestamp", "receivingTime", "processingTime", "opportunityFound", "providerName"]
    # result_log_path = "./logs/node_latency.csv"
    # result_log = open(result_log_path, "a")
    # results = {'blockNumber': 11250929, 'blockTimestamp': 1605291503, 'receivingTime': 1605291548, 'processingTime': 0.19970107078552246, 'opportunityFound': False, 'providerName': 'infura'}
    # writer = csv.DictWriter(result_log, fieldnames=fieldnames)
    # writer.writerow(results)
    # # result_log.close()