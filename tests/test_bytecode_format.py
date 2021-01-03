# Check if the bytecode fits with dispatcher

from tests.test_arbbot import test_form_bytecode
import src.config as cf
from src.ganache import Ganache
from arbbot.main import ArbBot
from src.helpers import approve_erc20, execute_payload, balance_erc20

from web3 import Web3
import web3
from pprint import pprint
import atexit


def test_bytecode_format(bytecode):
    dispatcher = w3.eth.contract(abi=cf.abi("dispatcher_trader"), 
                                 address=cf.address("dispatcher"))
    _, decoded = dispatcher.decode_function_input(bytecode)
    # print(type(decoded["queryScript"]))
    decoded["queryScript"] = bytearray(decoded["queryScript"]).hex()
    decoded["executeScript"] = bytearray(decoded["executeScript"]).hex()
    # pprint(decoded["queryScript"])
    # exit()
    return make_trade(**decoded)


def make_trade(queryScript, queryInputLocations, executeScript, executeInputLocations, targetPrice, ethValue):
    prices = query_all_prices(w3, queryScript, queryInputLocations)
    if not int(prices[-1], 16) > targetPrice:
        raise "Not profitable"
    for i in range(len(executeInputLocations)):
        print(f"replace with {prices[i]} at {executeInputLocations[i]}")
        executeScript = replace_data_at(executeScript, prices[i], executeInputLocations[i])
        pprint(executeScript)
    return execute(executeScript, ethValue)



def execute(script, ethValue):
    location = 0
    while (location < len(script)):
        contractAddress = address_at(script, location)
        calldataLength = uint256_at(script, location + 40)
        calldataStart = location + 40 + 64
        callData = script[calldataStart:calldataStart+calldataLength]
        if location == 0:
            call_method(contractAddress, callData, ethValue)
        else:
            call_method(contractAddress, callData, 0)
        location += (40 + 64 + calldataLength)


def query_all_prices(w3, script, inputLocations):
    location = 0
    lastPrice = 0
    prices = []
    inputsLength = len(inputLocations)
    inputsIndex = 0
    while (location < len(script)):
        contractAddress = address_at(script, location)
        calldataLength = uint256_at(script, location + 40)
        calldataStart = location + 40 + 64
        if (location != 0 and inputsLength > inputsIndex):
            insertLocation = inputLocations[inputsIndex]
            script = replace_data_at(script, lastPrice, insertLocation)
            inputsIndex += 1
        
        callData = script[calldataStart: calldataStart+calldataLength]
        lastPrice = getPrice(w3, contractAddress, callData)
        prices.append(lastPrice)
        location += (40 + 64 + calldataLength)
    
    return prices


# def query_all_prices(script, inputLocations):
#     contract = w3.eth.contract(abi=cf.abi("dispatcher_queryEngine"), address=cf.address("dispatcher_queryEngine"))
#     r = contract.functions.queryAllPrices(script, inputLocations).call()
#     r = r.hex()
#     print(r)
#     r = [r[i:i+64] for i in range(0,len(r),64)]
#     return r


def replace_data_at(original, new_bytes, location):
    location *= 2
    return original[:location] + new_bytes + original[location+64:]


def address_at(script, location):
    return script[location:location+40]


def uint256_at(script, location):
    return int(script[location:location+64], 16)*2


def call_method(contract_address, calldata, eth_value):
    pprint(calldata)
    contract_address = Web3.toChecksumAddress(contract_address)
    calldata = "0x" + calldata

    tx = {
          "data": calldata, 
          "value": eth_value, 
          "to": contract_address, 
          "from": wallet_address,
          "gas": 2000000, 
          "gasPrice": 100
          }
    pprint(tx)
    _submit_tx(tx)
    bal = w3.eth.getBalance(wallet_address) / 10**18
    print(calldata)
    print(bal)
    print(balance_erc20(w3, wallet_address, "0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44", convert=1))

def _submit_tx(tx):
    tx_hash = w3.eth.sendTransaction(tx).hex()
    receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    return receipt

def execute_approval(spender, tkn_address, gas_price=None):
    tx = approve_erc20(tkn_address, spender)
    tx_hash = execute_payload(w3, tx, wallet_address, gas_price=gas_price)
    results = w3.eth.waitForTransactionReceipt(tx_hash)
    return results

def getPrice(w3, contract_address, calldata):
    contract_address = Web3.toChecksumAddress(contract_address)
    query_engine_address = "0x62e34F7D2bB56C1c37a2C21fa89d0cf1291cf7D1"
    contract = w3.eth.contract(abi=cf.abi("dispatcher_queryEngine"), address=query_engine_address)
    price = contract.functions.getPrice(contract_address, calldata).call()

    return price.hex()


def get_ganache_web3(target_block, provider_name):
    global wallet_address
    unlocked = [cf.address("archerDAOClient")]
    provider_path = cf.provider(provider_name).html_path
    start_block_number = target_block-1 if target_block else None
    ganache_session = Ganache(provider_path, block_number=start_block_number, mine_interval=3, unlock=unlocked)
    ganache_session.start_node()
    wallet_address = ganache_session.accounts[0]
    atexit.register(lambda: ganache_session.kill())  # Closes the node after python session is finished
    return Web3(Web3.HTTPProvider(ganache_session.node_path))


if __name__ == "__main__":
    provider_name = "chainStackBlocklytics"
    # w3 = cf.web3_api_session(provider_name)
    # tx_bytecode = test_form_bytecode()
    w3 = get_ganache_web3(11546663, provider_name)
    bot = ArbBot(w3, handler_address=wallet_address)
    gas_prices = {"rapid": 120}
    print(wallet_address)
    execute_approval(cf.address("sushiswap_router"), "0x1cEB5cB57C4D4E2b2433641b95Dd330A33185A44", gas_price=gas_prices["rapid"])
    bal = w3.eth.getBalance(wallet_address) / 10**18
    print(bal)
    result = bot(11546663, 1609214945, gas_prices)
    # print(result)
    test_bytecode_format(result["bytecode"])

