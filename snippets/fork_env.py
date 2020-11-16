from web3 import Web3
from config import *

def uniswap(pool_address, input_amount, inverse=False):
    FEE = 0.003
    uni_pool = w3.eth.contract(address=pool_address, abi=ABIS["uniswapv2"])
    bal0, bal1, _ = uni_pool.functions.getReserves().call()
    if inverse: bal0, bal1 = bal1, bal0
    bal0 /= 10**18  # This can depend on the token
    bal1 /= 10**18  # This can depend on the token
    amount_out = (1 - bal1/(bal1+input_amount)) * bal0 * (1-FEE)
    
    return amount_out

GANACHE_URL = "127.0.0.1:7575"
alice = "0xF4D408D95a88b0aCaBe1443931f0e66fa58aD24B"
bob = "0x28ada978ca6153217884D62Bd7d8F9B25Da7b665"
halfrekt_address = ADDRESSES["halfrekt"]["halfrekt"]
halfrekt_abi = ABIS[halfrekt_address]
w3 = Web3(Web3.HTTPProvider("http://"+GANACHE_URL))
print(w3.eth.blockNumber)

half_rekt = w3.eth.contract(address=halfrekt_address, abi=halfrekt_abi)
target = half_rekt.functions.nextExploitBlock().call()+1  # The executing block needs to be greater than nextExploitBlock
print(target)     
half_rekt = w3.eth.contract(address=halfrekt_address, abi=halfrekt_abi)
exp_bal = half_rekt.functions.balanceOf(ADDRESSES["halfrekt"]["exploiter"]).call()
reward_nme = exp_bal * 0.001 * 10**-18
reward_eth = uniswap(ADDRESSES["uniswap"]["ethnme"], reward_nme, inverse=1)
print(reward_nme)
print(reward_eth)



      
# UNISWAP_ROUTER = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
# WETH9 = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
# HALFREKT = "0x404A03728Afd06fB934e4b6f0EaF67796912733A"
# GAS_AMOUNT_TRADE = 200000
# trade_payload = {"contractAddress": HALFREKT, 
#                  "function": "swapExactTokensForTokens", 
#                  "args": [amount_in, amount_out*(1-slippage), [HALFREKT, WETH9], env_vals['ADDRESS'], deadline], 
#                  "gasLimit": GAS_AMOUNT_TRADE
#                  }
# half_rekt = w3.eth.contract(address=HALFREKT, abi=ABIS[HALFREKT])

# tx1 = {
# 	    "nonce": w3.eth.getTransactionCount(MY_ADDRESS),
# 	    "gasPrice": gas_prices[0],
# 	    "gas": gas_amount,
# 	    "from": MY_ADDRESS,
# 	    "to": CONTRACT_ADDRESS,
# 	    "value": 0,
# 	    "data": '0x4df6f0c0'
# }	



# tx_hash = contract.functions.transfer(bob, 100).transact({'from': alice})
# tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
# alice_balance = contract.functions.balanceOf(alice).call()
# bob_balance = contract.functions.balanceOf(alice).call()
# print(alice_balance, bob_balance)