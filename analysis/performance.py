import time
from pprint import pprint
import pandas as pd
import csv
import atexit

from src.config import *
from src.opportunities import EmptySet


class DummyEmptySetContract():


    class Method():

        def __init__(self, method):
            self.method = method

        def call(self):
            return self.method()

        def epoch(self):
            return self

    def __init__(self, real_contract, past_data, get_current_timestamp):
        self.contract = real_contract
        self.past_data = past_data
        self.start_epoch = self._get_start_epoch()
        self.get_current_timestamp = get_current_timestamp
        self.functions = self.Method(self._get_epoch)

    def _get_start_epoch(self):
        return EmptySet.calc_epochTime(self.past_data.iloc[0].timestamp)-1

    def _get_epoch(self):
        df = self.past_data
        # Note! block_timestamp should be global
        current_timestamp = self.get_current_timestamp()
        epoch_count = len(df[df.timestamp <= current_timestamp])
        current_epoch = self.start_epoch + epoch_count
        
        # Account for the time that takes to call the method
        self.contract.functions.epoch().call()

        return current_epoch

    def encodeABI(self, fn_name=None, args=[]):
        return self.contract.encodeABI(fn_name=fn_name, args=args)

    def functions():
        return Method(self._get_epoch)


def loop(opp, block_number):
    global CURRENT_TIMESTAMP
    block_info = w3.eth.getBlock(block_number)
    CURRENT_TIMESTAMP = block_timestamp = block_info.timestamp

    t1 = time.time()
    payload = opp(block_number, block_timestamp)
    t2 = time.time()
    pprint(payload)


    new_row = {"blockNumber": block_number,
               "blockTimestamp": block_timestamp,
               "timeLeft": es.nextEpochTimestamp - block_timestamp,
               "epoch": es.epoch,
               "tmDiff": t2 - t1, 
               "oppDetected": bool(payload)}

    return new_row


def main():
    global CURRENT_TIMESTAMP, w3, es
    CURRENT_TIMESTAMP = 0  # Global

    # Logger settings
    file_name = "./logs/performance.csv"
    perf_file =  open(file_name, "a")
    atexit.register(lambda: perf_file.close())
    column_names = ["blockNumber", "blockTimestamp", "timeLeft", "epoch", "tmDiff", "oppDetected"]
    writer = csv.DictWriter(perf_file, fieldnames=column_names)
    writer.writeheader()
    # Web3 Settings
    provider_name = "quickNode"
    html_provider = NODE_INFO[provider_name]["html_path"]
    w3 = Web3(Web3.HTTPProvider(html_provider))

    es = EmptySet(w3)  # It is global
    opp_blocks_df = get_past_opp()  # Df containing past tx for this opportunity
    opp_blocks = list(opp_blocks_df.itertuples(index=False))
    # Create dummy contract to replicate calls to the historical chain states
    es.emptyset_contract = DummyEmptySetContract(es.emptyset_contract, opp_blocks_df, get_current_timestamp)

    # Loop through all the blocks where opportunity was found
    for opp_block in opp_blocks:
        for block_number in range(opp_block.number-3, opp_block.number+1):
            new_row = loop(es, block_number)
            writer.writerow(new_row)
            pprint(new_row)


def get_past_opp():
    df = pd.DataFrame(pd.read_csv("./logs/ESDpastTxData.csv"))
    df_cut = df[(df.value=="1000000000000000000") & (df.timeStamp >= 1602201600)][["blockNumber", "timeStamp"]].sort_values(by="blockNumber", ascending=True)
    df_cut.columns = ["number", "timestamp"]
    return df_cut


def get_current_timestamp():
    return CURRENT_TIMESTAMP


if __name__ == "__main__":
    main()




