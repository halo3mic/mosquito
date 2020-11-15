import requests
import pandas as pd 
from pprint import pprint
from dotenv import dotenv_values


secrets = dotenv_values("./.env")
address = "0xdF0Ae5504A48ab9f913F8490fBef1b9333A68e68"
api_key = secrets["ETHERSCAN_TOKEN"]
payload = {"module": "account",
           "action": "tokentx",
           "address": address,
           "startblock": 10722660,
           "endblock": 999999999,
           "sort": "asc",
           "apikey": api_key
           }
response = requests.get('https://api.etherscan.io/api', payload).json()
txs = response["result"]
df = pd.DataFrame(txs)
df_trun = df[(df.tokenSymbol=="ESD")]
df_trun = df_trun[["blockNumber", "timeStamp", "contractAddress", "from", "gasUsed", "gasPrice", "value"]]
df_trun.to_csv("./logs/ESDpastTxData.csv")
pprint(df_trun)