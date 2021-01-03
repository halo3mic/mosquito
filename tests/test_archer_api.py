import requests

import src.config as cf


url = "https://api.archerdao.io"
headers =  {"x-api-key": cf.archer_api_key}
path = "/submit-opportunity"
 
payload = {
  "bot_id": "2", #  ID of bot
  "target_block": "1230000", #  Target block where you'd like the trade to take place
  "trade": "0x123435445996985686889393939494859485983693634643546", #  bytecode for trade
  "estimated_profit_before_gas": "50000000", #  expected profit in wei before accounting for gas
  "gas_estimate": "1000000", #  Expected gas usage of trade
  "query": "0x3487508640586506070676700098876", #  OPTIONAL: query bytecode to run before trade
  "query_breakeven": "4500000",# / OPTIONAL: query return value minimum to continue with trade
  "input_amount": "5000000", #  OPTIONAL: value to withdraw from dispatcher liquidity
  "input_asset": "ETH", #  OPTIONAL: asset to withdraw from dispatcher liquidity
  "query_insert_locations": [54, 128, 220], #  OPTIONAL: locations in query to insert values
  "trade_insert_locations": [56, 200] #  OPTIONAL: location in trade to insert values
}
r = requests.post(url+path, params=payload, headers=headers)
print("URL + path:")
print(url+path)
print()
print("Payload:")
print(payload)
print()
print("Header:")
print(headers)
print()
print("Response:")
print(r)