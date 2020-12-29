# Check if the bytecode fits with dispatcher

from tests.test_arbbot import test_form_bytecode
import src.config as cf

from web3 import Web3
import web3
from pprint import pprint


def test_bytecode_format(bytecode):
    dispatcher = w3.eth.contract(abi=cf.abi("dispatcher_trader"), 
                                 address=cf.address("dispatcher"))
    _, decoded = dispatcher.decode_function_input(bytecode)
    # print(type(decoded["queryScript"]))
    decoded["queryScript"] = bytearray(decoded["queryScript"]).hex()
    decoded["executeScript"] = bytearray(decoded["executeScript"]).hex()
    # pprint(decoded["queryScript"])
    # exit()
    make_trade(**decoded)


def make_trade(queryScript, queryInputLocations, executeScript, executeInputLocations, targetPrice, ethValue):
    prices = query_all_prices(queryScript, queryInputLocations)
    if not int(prices[:-64], 16) > targetPrice:
        raise "Not profitable"
    for i in range(len(executeInputLocations)):
        replace_data_at(executeScript, prices[i*64, (i+1)*64], executeInputLocations[i])
    execute(executeScript, ethValue)


def execute(script, ethValue):
    location = 0
    while (location < len(script)):
        contractAddress = address_at(script, location)
        calldataLength = uint256_at(script, location + 20)
        calldataStart = location + 40 + 64
        callData = script[calldataStart:calldataStart+calldataLength]
        if location == 0:
            call_method(contractAddress, callData, ethValue)
        else:
            call_method(contractAddress, callData, 0)
        location += (40 + 64 + calldataLength)


def query_all_prices(script, inputLocations):
    location = 0
    lastPrice = 0
    prices = []
    inputsLength = len(inputLocations)
    inputsIndex = 0
    while (location < len(script)):
        contractAddress = address_at(script, location)
        calldataLength = uint256_at(script, location + 20)
        calldataStart = location + 40 + 64
        if (location != 0 and inputsLength > inputsIndex):
            insertLocation = inputLocations[inputsIndex]
            replace_data_at(script, lastPrice, insertLocation)
            inputsIndex += 1
        
        callData = script[calldataStart: calldataStart+calldataLength]
        lastPrice = getPrice(contractAddress, callData)
        prices = prices.append(lastPrice)
        location += (40 + 64 + calldataLength)
    
    return prices


# def query_all_prices(script, inputLocations):
#     contract = w3.eth.contract(abi=cf.abi("dispatcher_queryEngine"), address=cf.address("calebsDispatcher"))
#     r = contract.functions.queryAllPrices(script, inputLocations).call()
#     print(r)
#     return r


def replace_data_at(original, new_bytes, location):
    location *= 2
    return original[:location] + new_bytes + original[location+64:]


def address_at(script, location):
    location *= 2
    return script[location:location+40]


def uint256_at(script, location):
    location *= 2
    return int(script[location:location+64], 16)*2


def call_method(contract_address, calldata, eth_value):
    tx = {"contractAddress": contract_address, 
          "calldata": calldata, 
          "ethValue": eth_value}
    pprint(tx)


def get_amount_out(router_address, input_amount, from_token, to_token):
    proxy_contract = w3.eth.contract(address=cf.address("uniswapv2_router_proxy"), abi=cf.abi("uniswapv2_router_proxy"))
    amount_out = proxy_contract.functions.getOutputAmount(router_address, input_amount, from_token, to_token).call()
    return amount_out

# def get_amount_out(router_address, input_amount, from_token, to_token):
#     proxy_contract = w3.eth.contract(address=router_address, abi=cf.abi("uniswapv2_router"))
#     return proxy_contract.functions.getAmountsOut(input_amount, [from_token, to_token]).call()


def getPrice(contract_address, calldata):
    contract_address = Web3.toChecksumAddress(contract_address)
    print(calldata)
    print(contract_address)

    input_amount_decimal = int("00000000000000000000000000000000000000000000000030927f74c9de0000", 16)
    print(f"Input amount dec: {input_amount_decimal}")
    tkn1 = Web3.toChecksumAddress("c02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
    tkn2 = Web3.toChecksumAddress("2260fac5e5542a773aa44fbcfedf7c193bc2c599")
    amount_out = get_amount_out("0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D", input_amount_decimal, tkn1, tkn2)
    print(f"Output amount dec: {amount_out}")

    # calldata = bytes(calldata.encode())
    calldata = "0x73c9a010" + calldata[8:]
    pprint(calldata)
    contract = w3.eth.contract(abi=cf.abi("dispatcher_queryEngine"), address=cf.address("dispatcher"))

    price = contract.functions.getPrice(contract_address, calldata)
    print(price)
    exit()
    # return price



if __name__ == "__main__":
    provider_name = "chainStackBlocklytics"
    w3 = cf.web3_api_session(provider_name)
    tx_bytecode = test_form_bytecode()
    test_bytecode_format(tx_bytecode)
    # address = "0x67B66C99D3Eb37Fa76Aa3Ed1ff33E8e39F0b9c7A"
    # calldata = "6e616d650a"
    # tx = {'value': 0, 'gas': 40000, 'gasPrice': 80, 'to': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D', 'data': '0x666163746f72792829'}
    # print(w3.eth.call(tx))
