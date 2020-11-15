from src.config import *
import src.helpers as hp

from pprint import pprint
import time


provider = NODE_INFO["infura"]["html_path"]
w3 = Web3(Web3.HTTPProvider(provider))

def test_balance_erc20():
    dai_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    balance = hp.balance_erc20(w3, "0xCFb13c3248887Ab43d1777b63E57a84e8250A033", dai_address)
    print(balance)

def test_uniswap_get_payload1():
    input_amount = 100*10**18
    amount_out_min = input_amount*0.8
    to_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
    path = ["0x36F3FD68E7325a35EB768F1AedaAe9EA0689d723", "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"]
    
    uni = hp.Uniswap(w3)
    payload = uni.get_payload(input_amount, 0.2, path, 400000, to_address)
    return payload

def test_uniswap_get_payload2():
    input_amount = 100*10**18
    amount_out_min = input_amount*0.8
    to_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
    path = ["0x6B175474E89094C44Da98b954EedeAC495271d0F", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"]
    
    uni = hp.Uniswap(w3)
    payload = uni.get_payload(input_amount, 0.2, path, 400000, to_address)
    return payload


def test_payload2bytes():
    payload = {'blockNumber': 11258078,
               'botId': 'MSQT1',
               'estimatedProfit': 2.2761484197384675e+17,
               'gasEstimate': 380000,
               'profitCurrency': 'ETH',
               'supplierAddress': '0xCFb13c3248887Ab43d1777b63E57a84e8250A033',
               'txs': [{'calldata': '0xea105ac7',
                        'contractAddress': '0x443D2f2755DB5942601fa062Cc248aAA153313D3',
                        'gasLimit': 400000},
                       {'calldata': '0x18cbafe50000000000000000000000000000000000000000000000000000000000000064000000000000000000000000000000000000000000000000032090590f71778000000000000000000000000000000000000000000000000000000000000000a00000000000000000000000002493336e00a8adfc0eedd18961a49f2acaf8793f000000000000000000000000000000000000000000000000000000005fb0432b000000000000000000000000000000000000000000000000000000000000000300000000000000000000000036f3fd68e7325a35eb768f1aedaae9ea0689d723000000000000000000000000a0b86991c6218b36c1d19d4a2e9eb0ce3606eb48000000000000000000000000c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2',
                        'contractAddress': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
                        'gasLimit': 400000}]}
    tx_bytes = hp.payload2bytes(payload)

    return tx_bytes

    

t0 = time.time()
result = test_payload2bytes()
print(time.time()-t0)
pprint(result)