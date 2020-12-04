import src.config as cf
import time
import atexit
import codecs
import requests


def approve_erc20(token_address, spender, amount=-1):
    amount = "f"*64 if amount==-1 else hex(amount).split("x")[1]
    calldata = "0x095ea7b3" + spender.lower().split("x")[1].zfill(64) + amount.zfill(64)
    payload = {"contractAddress": token_address, 
               "calldata": calldata, 
               "gasLimit": 70000}
    return payload


def transfer_erc20(token_address, reciver, amount):
    calldata = "0xa9059cbb" + reciver.lower().split("x")[1].zfill(64) + hex(amount).split("x")[1].zfill(64)
    payload = {"contractAddress": token_address, 
               "calldata": calldata, 
               "gasLimit": 50000}
    return payload


def balance_erc20(w3, holder_address, token_address):
    tkn_contract = w3.eth.contract(address=token_address, abi=cf.abi("erc20_token"))
    decimals = tkn_contract.functions.decimals().call()
    balance = tkn_contract.functions.balanceOf(holder_address).call()
    return balance / 10**decimals


def payload2bytes(payload):
    def str2hex(text):
        return codecs.encode(text.encode(), "hex").decode()

    def int2hex(digit):
        return format(int(digit), "x")

    def prepare(arg, atype):
        methods = {"a": lambda x: x.split("x")[1].zfill(64), 
                   "i": lambda x: int2hex(x).zfill(64), 
                   "s": lambda x: str2hex(x).zfill(64)}
        return methods[atype](arg)

    args = [("botId", "s"), 
            ("supplierAddress", "a"), 
            ("blockNumber", "i"), 
            ("gasEstimate", "i"), 
            ("estimatedProfit", "i"), 
            ("profitCurrency", "s")]
    
    byteload = ""
    for key, atype in args:
        byteload += prepare(payload[key], atype)
    byteload += prepare(len(payload["txs"]), "i")

    for tx in payload["txs"]:
        calldata = tx["calldata"].split("x")[1]
        calldata_length = prepare(len(calldata)//2, "i")
        contract_address = prepare(tx["contractAddress"], "a")
        gas_limit = prepare(tx["gasLimit"], "i")
        tx_bytes = contract_address + gas_limit + calldata_length + calldata.zfill(64)
        byteload += tx_bytes

    return byteload


def execute_payload(w3, payload, wallet_address):
    # gas_price = w3.eth.gasPrice
    # nonce = w3.eth.getTransactionCount(wallet_address)
    # Add option to sign the tx
    tx = {
          "gasLimit": payload["gasLimit"],
          "from": wallet_address,
          "to": payload["contractAddress"],
          "data": payload["calldata"]}
    tx_hash = w3.eth.sendTransaction(tx).hex()
    
    return tx_hash  


def send2archer(byteload):
    payload = {"id": cf.bot_id, "byteload": byteload}
    print(cf.archer_api_endpoint)
    print(payload)
    r = requests.post(cf.archer_api_endpoint, payload)
    print(r)
    return r


