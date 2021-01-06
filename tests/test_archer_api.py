import requests
import json

import src.config as cf
import src.helpers as hp


url = "https://api.archerdao.io"
version_num = "/v1"
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
# payload["query_insert_locations"] = [{'location': str(l), 'param_sub_type': 'input'} for l in payload["query_insert_locations"]]
# payload["trade_insert_locations"] = [{'location': str(l), 'param_sub_type': 'input'} for l in payload["trade_insert_locations"]]

r = hp.send2archer(payload)
# print(json.dumps(payload))
# r = requests.post(url+version_num+path, data=json.dumps(payload), headers=headers)
# print("Full path:")
# print(url+version_num+path)
# print()
# print("Payload:")
# print(payload)
# print()
# print("Header:")
# print(headers)
# print()
print("Response:")
print(r)