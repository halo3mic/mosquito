import time
import atexit
import requests
from pprint import pprint

from src.config import *
from src.dev_main import execute, ws_receiver
from src.ganache import start_ganache
from src.opportunities import HalfRekt
from src.helpers import Uniswap, approve_erc20, transfer_erc20


def _get_epochTime():
    et = emptyset_contract.functions.epochTime().call()
    STORAGE["epoch_time"] = et
    return et


def _next_epoch_timestamp(epoch_time):
    return (epoch_time+1-CURRENT_EPOCH_OFFSET)*CURRENT_EPOCH_PERIOD+CURRENT_EPOCH_START


def is_epoch(blockTimestamp):
    epochTime_calc = (blockTimestamp-CURRENT_EPOCH_START)/CURRENT_EPOCH_PERIOD+CURRENT_EPOCH_OFFSET
    epochTime_request = STORAGE.get("epoch_time", _get_epochTime())
    return int(epochTime_calc) > epochTime_request


def opp_check(msg_org):
    msg = json.loads(msg_org)["params"]["result"]
    block_number = int(msg["number"].lstrip("0x"), 16)
    timestamp = int(msg["timestamp"].lstrip("0x"), 16) 
    if is_epoch(block_timestamp):
        print("letss gooo!!!")
    else:
        print("lets wait")


emptyset_address = ADDRESSES["emptyset"]["implementation"]
emptyset_abi = ABIS[emptyset_address]

node_path = NODE_INFO["alchemy"]["html_path"]
w3 = Web3(Web3.HTTPProvider(node_path))

emptyset_contract = w3.eth.contract(address=emptyset_address, abi=emptyset_abi)

CURRENT_EPOCH_START = 1602201600
CURRENT_EPOCH_PERIOD = 28800
CURRENT_EPOCH_OFFSET = 106

block_timestamp = w3.eth.getBlock("latest").timestamp

node_path = NODE_INFO["alchemy"]["ws_path"]
data_request = NODE_INFO["alchemy"]["ws_blocks_request"]
ws_receiver(node_path, data_request, opp_check)