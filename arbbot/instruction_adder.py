import src.config as cf
import pandas as pd
from web3 import Web3
from pprint import pprint
import sys


class InstructionAdder:

    def __init__(self):
        self.instr_mg = InstructionManager()
        self.pool_mg = PoolManager()
        self.tkn_mg = TokenManager()

    def add_token(self, data):
        pass

    def add_token(self, data):
        pass


class InstructionManager:
    
    token_storage_path = "./config/instructions.csv"

    def __init__(self):
        self.instr_df = None

    def get_instr_by_id(self, id):
        pass

    def get_instr_by_symbol(self, symbol):
        pass
    
    def add_instr(self, data):
        pass

    def _generate_new_id(self):
        pass


class PoolManager:
    
    token_storage_path = "./config/pools.csv"

    def __init__(self):
        self.pool_df = None

    def get_pool_by_id(self, id):
        pass

    def get_pool_by_symbol(self, symbol):
        pass
    
    def add_pool(self, data):
        pass

    def _generate_new_id(self):
        pass


class TokenManager:
    
    token_storage_path = "./config/tokens.csv"

    def __init__(self):
        self.tkn_df = pd.read_csv(self.token_storage_path)

    def get_tkn_by_id(self, id):
        filtered = self.tkn_df[self.tkn_df.id==id]
        if not len(filtered):
            return 
        elif len(filtered)>1:
            raise Exception(f"More than one token with id {id}")
        return filtered

    def get_tkn_by_symbol(self, symbol):
        filtered = self.tkn_df[self.tkn_df.symbol==symbol]
        if not len(filtered):
            return 
        elif len(filtered)>1:
            raise Exception(f"More than one token with symbol {symbol}")
        return filtered

    def add_token(self, data):
        # Check if tkn already exists by symbol or id
        by_symbol = self.get_tkn_by_symbol(data["symbol"])
        if by_symbol:
            raise Exception("Token already added!")
        # Generate id for the token
        data["id"] = self._generate_new_id()

        df = self.tkn_df.append(data, ignore_index=True)
        df.to_csv(self.token_storage_path)

        msg = "New token saved"
        print(msg.center(70, "*"))
        pprint(data)
        print("*"*70)

    def _generate_new_id(self):
        count = self.tkn_df
        new_id = "T" + str(count+1).zfill(4)
        return new_id




class QueryChain:

    def __init__(self, provider_name):
        self.w3 = cf.web3_api_session(provider_name)

    def query_unisus_pool(self, pool_address):
        exchange_symbol_dict = {"UNI-V2": "uniswap", "SLP": "sushiswap"}
        fee = 0.003
        try:
            pool_address = Web3.toChecksumAddress(pool_address)
            pool_contract = self.w3.eth.contract(address=pool_address, abi=cf.abi("uniswapv2"))
            exchange = pool_contract.functions.symbol().call()
            exchange = exchange_symbol_dict[exchange]
            tkn1 = pool_contract.functions.token0().call()
            tkn2 = pool_contract.functions.token1().call()
            tkns = tkn1, tkn2
            pool_info = {"fee": fee, "tokens": tkns, "address": pool_address, "exchange": exchange}
        except ValueError:
            raise Exception("Invalid pool address")

        return pool_info

    # def query_pool(self, pool_address, exchange=None):
    #     # Later add balancer and bancor functions and if no exchange specified
    #     # then try to find the right function by trial and error
    #     exchange = exchange.lower()
    #     try:
    #         pool_address = Web3.toChecksumAddress(pool_address)
    #         if exchange in ("uniswap", "sushiswap"):
    #             pool_info = self.query_unisus_pool(pool_address)
    #             return pool_info
    #     except ValueError:
    #         raise Exception("Invalid pool address")

    def query_token(self, token_address):
        # Only for ERC20 tokens!
        token_address = Web3.toChecksumAddress(token_address)
        pool_contract = self.w3.eth.contract(address=token_address, abi=cf.abi("erc20_token"))
        symbol = pool_contract.functions.symbol().call()
        decimal = pool_contract.functions.decimals().call()
        token_info = {"symbol": symbol, "decimal": decimal, "address": token_address}
        return token_info

