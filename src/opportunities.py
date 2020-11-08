from src.config import *
from src.helpers import Uniswap, approve_erc20


class EmptySet:

    EPOCH_START = 1602201600
    EPOCH_PERIOD = 28800
    EPOCH_OFFSET = 106

    def __init__(self, web3, wallet_address):
        self.wallet_address = wallet_address
        self.gas_limit_advance = 400000
        self.gas_limit_trade = 400000
        self.payloads = []

        self.emptyset_proxy = ADDRESSES["emptyset"]["proxy"]
        self.emptyset_implementation = ADDRESSES["emptyset"]["implementation"]
        self.emptyset_contract = web3.eth.contract(address=self.emptyset_proxy, abi=ABIS[self.emptyset_implementation])
        self.uniswap = Uniswap(web3)

    def __str__(self):
        return "EmptySet"

    def __call__(self, block_number, block_timestamp):
        if self.is_epoch(block_timestamp):
            payloads = self.get_payloads()
            return payloads

    def _get_target_timestamp(self, epoch_time):
        tm = (epoch_time+1-EmptySet.EPOCH_OFFSET)
        tm *= EmptySet.EPOCH_PERIOD
        tm += EmptySet.EPOCH_START
        return tm

    def get_payloads(self):
        emptyset_calldata = self.emptyset_contract.encodeABI(fn_name="advance", args=[])
        emptyset_payload = {"contractAddress": self.emptyset_proxy, 
                            "calldata": emptyset_calldata, 
                            "gasLimit": self.gas_limit_advance
                            }
        path = [ADDRESSES["tokens"]["esd"], ADDRESSES["tokens"]["usdc"], ADDRESSES["tokens"]["weth9"]]
        trade_payload = self.uniswap.get_payload(100*10**18, 
                                                 0, # Specify better price otherwise this could fail
                                                 path, 
                                                 self.gas_limit_trade, 
                                                 to_address=self.wallet_address, tkn_slippage=0.5)

        return self.payloads + [emptyset_payload, trade_payload]

    def _get_epochTime(self):
        et = self.emptyset_contract.functions.epochTime().call()
        STORAGE["epoch_time"] = et
        return et

    def _get_epoch(self):
        et = self.emptyset_contract.functions.epoch().call()
        STORAGE["epoch"] = et
        return et

    def is_epoch(self, blockTimestamp):
        epochTime_calc = (blockTimestamp-EmptySet.EPOCH_START)
        epochTime_calc /= EmptySet.EPOCH_PERIOD
        epochTime_calc += EmptySet.EPOCH_OFFSET
        epochTime_call = STORAGE.get("epochTime", self._get_epochTime())
        epochTime = int(epochTime_calc)
        epoch = STORAGE.get("epoch", self._get_epoch())
        print("epoch: ", epoch)
        print("calcEpochTime: ", epochTime_calc)
        print("epochTime: ", epochTime)
        print("epochTime_call:", epochTime_call)
        print("target_timestamp: ", self._get_target_timestamp(epochTime))
        # what is the threshold -- when to fire it?
        return epoch < epochTime

class HalfRekt:

    def __init__(self, web3, wallet_address):
        self.web3 = web3
        self.wallet_address = wallet_address
        self.block_number = web3.eth.blockNumber
        self.gas_limit_rekt = 150000
        self.gas_limit_trade = 200000
        self.payout_nme = None
        self.payout_eth = None
        self.payloads = []

        self.halfrekt_address = ADDRESSES["halfrekt"]["halfrekt"]
        self.halfrekt_contract = web3.eth.contract(address=self.halfrekt_address, abi=ABIS[self.halfrekt_address])
        self.uniswap = Uniswap(web3)

        rem_allowance =  self.halfrekt_contract.functions.allowance(wallet_address, ADDRESSES["uniswap"]["uniswapv2_router02"]).call()
        if rem_allowance < 5000*10**18:
            payload = approve_erc20(self.halfrekt_address, ADDRESSES["uniswap"]["uniswapv2_router02"], 10000*10**18)
            self.payloads.append(payload)
    def __str__():
        return "HalfRekt"

    def __call__(self):
        # Check if the next exploit number is stored
        target = STORAGE.get("halfRekt_nextExploitBlockNumber", self._get_target())
        print("storage target: ", target)
        # If the next block is the target and doublecheck that opportunity is still available
        if target > self.block_number+1 or self._get_target() != target:
            print(target - self.block_number, " blocks left")
            return
        print("Opportunity found!!!")
        payout = self.query()
        payloads = self.get_payloads()
        return {"payout": payout, "payloads": payloads}

    def _get_target(self):
        target = self.halfrekt_contract.functions.nextExploitBlock().call()+1  # The executing block needs to be greater than nextExploitBlock
        STORAGE["halfRekt_nextExploitBlockNumber"] = target
        return target

    # NEED TO APPROVE BEFORE SWAP!!!
    def query(self):
        exp_bal = self.halfrekt_contract.functions.balanceOf(ADDRESSES["halfrekt"]["exploiter"]).call()
        self.payout_nme = exp_bal * 0.001 * 10**-18
        self.payout_eth = self.uniswap.get_amount_out(self.payout_nme, ADDRESSES["uniswap"]["ethnme"], inverse=1)
        # self.gas_cost = w3.eth.gasPrice * (self.gas_limit_rekt+self.gas_limit_trade) / 10**18

        return self.payout_eth

    def get_payloads(self):
        halfrekt_calldata = self.halfrekt_contract.encodeABI(fn_name="exploitTheExploiter", args=[])
        halfrekt_payload = {"contractAddress": self.halfrekt_address, 
                            "calldata": halfrekt_calldata, 
                            "gasLimit": self.gas_limit_rekt
                            }
        path = [self.halfrekt_address, ADDRESSES["tokens"]["weth9"]]
        trade_payload = self.uniswap.get_payload(self.payout_nme*10**18, 
                                                 0, 
                                                 path, 
                                                 self.gas_limit_trade, 
                                                 to_address=self.wallet_address, tkn_slippage=0.5)

        return self.payloads + [halfrekt_payload, trade_payload]


if __name__=="__main__":
    from pprint import pprint


    provider = NODE_INFO["infura"]["html_path"]
    w3 = Web3(Web3.HTTPProvider(provider))

    current_block = w3.eth.blockNumber
    hf = HalfRekt(current_block, w3, "0xFFA5bFe92B6791DAd23c7837abb790b48C2F8995")
    # payout = hf.query()
    # print(payout)
    # pprint(hf.get_payloads())
    response = hf()
    pprint(response)


    
