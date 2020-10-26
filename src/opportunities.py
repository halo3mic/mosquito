from config import *
from helpers import Uniswap, approve_erc20


class HalfRekt:

    def __init__(self, block_number, web3, wallet_address):
        self.web3 = web3
        self.wallet_address = wallet_address
        self.block_number = block_number
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


    
