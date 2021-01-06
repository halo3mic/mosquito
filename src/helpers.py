import src.config as cf
import time
import atexit
import codecs
import requests
from math import floor, log10
import csv
import json


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


def balance_erc20(w3, holder_address, token_address, convert=False):
    tkn_contract = w3.eth.contract(address=token_address, abi=cf.abi("erc20_token"))
    balance = tkn_contract.functions.balanceOf(holder_address).call()
    if convert:
        decimals = tkn_contract.functions.decimals().call()
        balance /= 10**decimals
    return balance


def erc20_approved(w3, tkn_address, owner, spender, convert=False):
    tkn_contract = w3.eth.contract(address=tkn_address, abi=cf.abi("erc20_token"))
    allowed = tkn_contract.functions.allowance(owner, spender).call()
    if convert:
        decimals = tkn_contract.functions.decimals().call()
        allowed /= 10**decimals
    return allowed


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


def tx2bytes(calldata, contract_address):
    calldata = calldata.split("x")[1]
    contract_address = contract_address.split("x")[1]
    calldata_length = format(len(calldata)//2, "x").zfill(64)
    tx_bytes = contract_address + calldata_length + calldata.zfill(64)

    return tx_bytes


def execute_payload(w3, payload, wallet_address, gas_price=None, wait4receipt=False):
    gas_price = w3.eth.gasPrice if not gas_price else gas_price
    # nonce = w3.eth.getTransactionCount(wallet_address)
    # Add option to sign the tx
    tx = {
          "gasLimit": payload["gasLimit"],
          "from": wallet_address,
          "to": payload["contractAddress"],
          "data": payload["calldata"], 
          "value": payload.get("value", 0)
          }
    if gas_price:
        tx["gasPrice"] = int(gas_price *10**9)
    tx_hash = w3.eth.sendTransaction(tx).hex()
    if wait4receipt:
        return w3.eth.waitForTransactionReceipt(tx_hash)

    return tx_hash


def round_sig(x, sig=4):
    """Return value rounded to specified significant figure"""
    if x==0:
        return 0
    rounded = round(x, sig - floor(log10(abs(x))) - 1)
    rounded = int(rounded) if float(rounded).is_integer() else rounded  # 1.0 --> 1
    return rounded


def save_logs(row_content, save_as):
    with open(save_as, "a") as log_file:
        writer = csv.DictWriter(log_file, fieldnames=row_content.keys())
        writer.writerow(row_content)


def remove_bytecode_data(bytecode, location, length=64):
    return bytecode[:location] + bytecode[location+length:]


def send2archer(payload):
    url = "https://api.archerdao.io"
    version_num = "/v1"
    path = "/submit-opportunity"
    full_path = url + version_num + path
    headers = {"x-api-key": cf.archer_api_key}
    # payload["query_insert_locations"] = [{'location': str(l), 'param_sub_type': 'input'} for l in payload["query_insert_locations"]]
    # payload["trade_insert_locations"] = [{'location': str(l), 'param_sub_type': 'input'} for l in payload["trade_insert_locations"]]
    payload["query_insert_locations"] = [str(v) for v in payload["query_insert_locations"]]
    payload["trade_insert_locations"] = [str(v) for v in payload["trade_insert_locations"]]
    payload["target_block"] = str(payload["target_block"])
    payload["estimated_profit_before_gas"] = str(payload["estimated_profit_before_gas"])
    payload["gas_estimate"] = str(payload["gas_estimate"])
    payload["query_breakeven"] = str(payload["query_breakeven"])
    payload["input_amount"] = str(payload["input_amount"])
    r = requests.post(full_path, data=json.dumps(payload), headers=headers)

    try:
        return r.json()
    except:
        return r



