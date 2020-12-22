import src.config as cf
from src.helpers import payload2bytes
from src.exchanges import Uniswap

import time


class EmptySet:

    EPOCH_START = 1602201600
    EPOCH_PERIOD = 28800
    EPOCH_OFFSET = 106
    tm_threshold = 20  # Threshold in seconds for when to trigger the opportunity
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
        self.last_opp_block = 0
        self.nextEpochTimestamp = 0
        self.epoch = None
        self.web3 = web3

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

    def target_timestamp(self):
        return self.nextEpochTimestamp

    def _get_epoch(self):
        et = self.emptyset_contract.functions.epoch().call()
        self.epoch = et
        return et

    def is_epoch(self, block_timestamp):
        if self.nextEpochTimestamp - block_timestamp <= self.tm_threshold:
            block_number = self.web3.eth.blockNumber
            if block_number == self.last_opp_block:
                return
            elif block_number-self.last_opp_block<10 or self.nextEpochTimestamp<block_timestamp:
                self.nextEpochTimestamp = self._get_target_timestamp()
            if self.nextEpochTimestamp - block_timestamp <= self.tm_threshold:
                self.last_opp_block = block_number
                return True

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

    def coupons(self):
        return self.emptyset_contract.functions.totalRedeemable().call()


class AlphaFinance: 


    def __init__(self, web3):
        self.web3 = web3

    def __str__(self):
        return "AlphaFinance"

    def __call__(self):
        worker = "0x4668fF4D478C5459d6023C4a7EfdA853412fb999"
        staking = "0x6C3e4cb2E96B01F4b866965A91ed4437839A121a"
        contract = self.web3.eth.contract(address=staking, abi=cf.abi(staking))
        earned = contract.functions.earned(worker).call()
        return earned

    def get_all_goblins(self):
        bank_address = cf.address("alpha_bank")
        bank_contract = self.web3.eth.contract(address=bank_address, abi=cf.abi(bank_address))
        goblins = set()
        c = 1
        while 1:
            goblin, *_ = bank_contract.functions.positions(c).call()
            if goblin=="0x0000000000000000000000000000000000000000":
                break
            goblins.add(goblin)
            print(goblin)
            c += 1

        return goblins


class ArbBot:

    def __init__(self):
        pass

    def import_state(self):
        pass

    def export_state(self):
        pass

    