from src.config import *
from src.helpers import payload2bytes
from src.opportunities import EmptySet
from pprint import pprint


provider_name = "infura"
wallet_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
html_provider = NODE_INFO[provider_name]["html_path"]
w3 = Web3(Web3.HTTPProvider(html_provider))
block_number = w3.eth.blockNumber
es = EmptySet(w3, wallet_address)
payload = es.get_payload(block_number)
byteload = payload2bytes(payload)

pprint(byteload)