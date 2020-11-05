from src.config import *
import src.helpers as hp

from pprint import pprint


provider = NODE_INFO["infura"]["html_path"]
w3 = Web3(Web3.HTTPProvider(provider))

def test_balance_erc20():
    dai_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    balance = hp.balance_erc20(w3, "0xCFb13c3248887Ab43d1777b63E57a84e8250A033", dai_address)
    print(balance)

def test_uniswap_get_payload():
    input_amount = 100*10**18
    amount_out_min = input_amount*0.8
    to_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
    path = ["0x36F3FD68E7325a35EB768F1AedaAe9EA0689d723", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"]
    
    uni = hp.Uniswap(w3)
    payload = uni.get_payload(input_amount, 0.2, path, 400000, to_address)
    return payload
    

# test_balance_erc20()
payload = test_uniswap_get_payload()
pprint(payload)