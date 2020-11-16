import src.config as cf
from src.helpers import payload2bytes
from src.exchanges import Uniswap

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
    wallet_address = cf.address("dispatcher_address")
    emptyset_proxy = cf.address("emptyset_proxy")
    emptyset_implementation = cf.address("emptyset_implementation")

    def __init__(self, web3):
        self.emptyset_contract = web3.eth.contract(address=self.emptyset_proxy, abi=cf.abi(self.emptyset_implementation))
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
        path = [cf.address("esd"), cf.address("usdc"), cf.address("weth9")]
        esd_reward = self.esd_reward * 10**cf.tkn_dec["esd"]
        reward_usdc = self.uniswap.get_amount_out(esd_reward, cf.address("uni_usdcesd"), inverse=1)
        reward_eth = self.uniswap.get_amount_out(reward_usdc, cf.address("uni_ethusdc"), inverse=1)
        trade_tx = self.uniswap.swapExactTokensForETH(self.esd_reward, 
                                                      reward_eth,
                                                      path, 
                                                      self.gas_limit_trade,
                                                      to_address=self.wallet_address)
        payload = {
                    "blockNumber": block_number, 
                    "gasEstimate": self.advance_gas_used + self.trade_gas_used, 
                    "supplierAddress": cf.address("supplier_address"), 
                    "botId": cf.bot_id, 
                    "txs": [emptyset_tx, trade_tx], 
                    "estimatedProfit": reward_eth,
                    "profitCurrency": "ETH"
                  }

        return payload

    def _get_target_timestamp(self):
        epoch = self._get_epoch()
        tm = (epoch+1-self.EPOCH_OFFSET)
        tm *= self.EPOCH_PERIOD
        tm += self.EPOCH_START
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
        self.opp_detected = (target_timestamp - block_timestamp) < self.tm_threshold 

        return self.opp_detected

    def import_state(self, data):
        for key, value in data.items():
            setattr(self, key, value)

    def export_state(self):
        return {"nextEpochTimestamp": self.nextEpochTimestamp}

    @staticmethod
    def calc_epochTime(block_timestamp):
        et = (block_timestamp-EmptySet.EPOCH_START)
        et /= EmptySet.EPOCH_PERIOD
        et += EmptySet.EPOCH_OFFSET
        et = int(et)
        return et

