import time
from pprint import pprint

from src.config import *
from src.dev_main import ws_receiver
from src.opportunities import EmptySet


provider_name = "infura"
wallet_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
html_provider = NODE_INFO[provider_name]["html_path"]
w3 = Web3(Web3.HTTPProvider(html_provider))
es = EmptySet(w3, wallet_address)
payload = es.get_payload(w3.eth.blockNumber)
pprint(payload["txs"][1]["calldata"])