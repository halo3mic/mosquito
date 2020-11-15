import time
from pprint import pprint
import pandas as pd
import csv

from src.config import *
from src.opportunities import EmptySet


provider_name = "localNode"
wallet_address = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
html_provider = NODE_INFO[provider_name]["html_path"]
w3 = Web3(Web3.HTTPProvider(html_provider))
es = EmptySet(w3, wallet_address)

df = pd.DataFrame(pd.read_csv("./logs/ESDpastTxData.csv"))
df_cut = df[["blockNumber", "timeStamp"]].sort_values(by="blockNumber", ascending=True)
df_cut.columns = ["number", "timestamp"]
opp_blocks = list(df_cut.itertuples(index=False))

# Cacluate start epoch
start_epoch = EmptySet.calc_epochTime(opp_blocks[0].timestamp-1)
es.STORAGE["epoch"] = start_epoch

# Loop through all the blocks where opportunity was found
file_name = "./logs/performance.csv"
with open(file_name, "a") as perf_file:
    column_names = ["blockNumber", "blockTimestamp", "timeLeft", "tmDiff", "oppDetected"]
    writer = csv.DictWriter(perf_file, fieldnames=column_names)
    # writer.writeheader()
    for opp_block in opp_blocks:
        for block_number in range(opp_block.number-4, opp_block.number+4):
            block_info = w3.eth.getBlock(block_number)
            print(block_number)
            t1 = time.time()
            payload = es(block_number, block_info.timestamp)
            t2 = time.time()

            if payload:
                es.STORAGE["epoch"] += 1
                es.STORAGE["nextEpochTimestamp"] = None

            new_row = {"blockNumber": block_number,
                       "blockTimestamp": block_info.timestamp,
                       "timeLeft": opp_block.timestamp - block_info.timestamp,
                       "tmDiff": t2 - t1, 
                       "oppDetected": bool(payload)}

            writer.writerow(new_row)
#         rows.append(new_row)

# df_perf = pd.DataFrame(rows)
# pprint(df_perf)




