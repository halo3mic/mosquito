from src.config import *
from src.helpers import Uniswap, approve_erc20, payload2bytes

import time


class EmptySet:

    EPOCH_START = 1602201600
    EPOCH_PERIOD = 28800
    EPOCH_OFFSET = 106
    tm_threshold = 15  # Threshold in seconds for when to trigger the opportunity
    esd_reward = 100
    advance_gas_used = 300000
    trade_gas_used = 200000
    gas_limit_advance = 400000
    gas_limit_trade = 400000
    wallet_address = DISPATCHER_ADDRESS

    @classmethod
    def calc_epochTime(cls, block_timestamp):
        et = (block_timestamp-EmptySet.EPOCH_START)
        et /= EmptySet.EPOCH_PERIOD
        et += EmptySet.EPOCH_OFFSET
        et = int(et)
        return et

    def __init__(self, web3):
        self.emptyset_proxy = ADDRESSES["emptyset"]["proxy"]
        self.emptyset_implementation = ADDRESSES["emptyset"]["implementation"]
        self.emptyset_contract = web3.eth.contract(address=self.emptyset_proxy, abi=ABIS[self.emptyset_implementation])
        self.uniswap = Uniswap(web3)
        self.opp_detected = False
        self.nextEpochTimestamp = None
        self.epoch = None

    def __str__(self):
        return "EmptySet"

    def __call__(self, block_number, block_timestamp):
        if self.is_epoch(block_timestamp):
            payload = self.get_payload(block_number)
            byteload = payload2bytes(payload)
            return byteload

    def get_payload(self, block_number):
        emptyset_calldata = self.emptyset_contract.encodeABI(fn_name="advance", args=[])
        emptyset_tx = {"contractAddress": self.emptyset_proxy, 
                            "calldata": emptyset_calldata, 
                            "gasLimit": self.gas_limit_advance
                            }
        path = [ADDRESSES["tokens"]["esd"], ADDRESSES["tokens"]["usdc"], ADDRESSES["tokens"]["weth9"]]
        uni_pools = ADDRESSES["uniswap"]
        esd_reward = EmptySet.esd_reward * 10**TKN_DECIMALS["esd"]
        reward_usdc = self.uniswap.get_amount_out(esd_reward, uni_pools["usdcesd"], inverse=1)
        reward_eth = self.uniswap.get_amount_out(reward_usdc, uni_pools["ethusdc"], inverse=1)
        trade_tx = self.uniswap.swapExactTokensForETH(EmptySet.esd_reward, 
                                                      reward_eth,
                                                      path, 
                                                      self.gas_limit_trade,
                                                      to_address=self.wallet_address)
        payload = {
                    "blockNumber": block_number, 
                    "gasEstimate": EmptySet.advance_gas_used + EmptySet.trade_gas_used, 
                    "supplierAddress": SUPPLIER_ADDRESS, 
                    "botId": BOT_ID, 
                    "txs": [emptyset_tx, trade_tx], 
                    "estimatedProfit": reward_eth,
                    "profitCurrency": "ETH"
                  }

        return payload

    def _get_target_timestamp(self):
        epoch = self._get_epoch()
        tm = (epoch+1-EmptySet.EPOCH_OFFSET)
        tm *= EmptySet.EPOCH_PERIOD
        tm += EmptySet.EPOCH_START
        self.nextEpochTimestamp = tm
        return tm

    def _get_epoch(self):
        et = self.emptyset_contract.functions.epoch().call()
        self.epoch = et
        return et

    def is_epoch(self, block_timestamp):
        target_timestamp = self.nextEpochTimestamp
        if not target_timestamp or self.opp_detected or (target_timestamp - block_timestamp < 0):
            target_timestamp = self.nextEpochTimestamp = self._get_target_timestamp()              
        self.opp_detected = (target_timestamp - block_timestamp) < EmptySet.tm_threshold 

        return self.opp_detected

    def import_state(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def export_state(self):
        return {"nextEpochTimestamp": self.nextEpochTimestamp}

