import time
from pprint import pprint

from src.config import *
from src.dev_main import ws_receiver
from src.opportunities import EmptySet


def process_input_w_log(msg_org):
    receiving_time = time.time()
    msg = json.loads(msg_org)["params"]["result"]
    block_number = int(msg["number"].lstrip("0x"), 16)
    timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
    t0 = time.time()
    opportunity_detected = check_plans(block_number, timestamp)
    t1 = time.time()
    processing_time = t1 - t0

    print(block_number)
    print(timestamp)
    print(receiving_time)
    print(processing_time)
    print(opportunity_detected)
    print(provider_name)


def check_plans(block_number, block_timestamp):
    payload = es(block_number, block_timestamp)
    return payload is not None


provider_name = "infura"
wallet_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
html_provider = NODE_INFO[provider_name]["html_path"]
ws_provider = NODE_INFO[provider_name]["ws_path"]
data_request = NODE_INFO[provider_name]["ws_blocks_request"]

w3 = Web3(Web3.HTTPProvider(html_provider))
es = EmptySet(w3, wallet_address)
# ws_receiver(ws_provider, data_request, process_input_w_log)
STORAGE["epoch"] = 195
curr_block = w3.eth.getBlock(11213398)
opp_detected = check_plans(curr_block.number, curr_block.timestamp)
print(opp_detected)


