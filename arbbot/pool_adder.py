import src.config as cf
import pandas as pd
from web3 import Web3
from pprint import pprint
import sys


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


class PoolAdder:

    def __init__(self, pools_path, tokens_path, provider):
        self.query_chain = QueryChain(provider)
        self.pools_path = pools_path
        self.tokens_path = tokens_path
        self.pools = pd.read_csv(pools_path)
        self.tokens = pd.read_csv(tokens_path)

    def add_pool(self, address, exchange=None):
        # Check if pool already added and get id
        pool_id = self._get_pool_id(address)
        if not pool_id:
            print(f"Pool {address} already added")
            return    
        # Gather info for new pool
        pool_info = self._fetch_pool_info(address, exchange)
        tkn_ids, tkn_symbols = zip(*[self._get_token_id_and_symbol(tkn) for tkn in pool_info["tokens"]])
        # Save_pool_info
        pool_info["id"] = pool_id
        pool_info["tokens"] = ", ".join(tkn_ids)
        pool_info["symbol"] = ''.join(tkn_symbols).lower()
        self._save_pool(pool_info)

    def _get_pool_id(self, address):
        matches = self.pools[self.pools.address==address]
        if len(matches):
            return None
        last_id = self.pools["id"].max()
        new_id = "P" + str(int(last_id.lstrip("P"))+1).zfill(4)
        return new_id

    def _fetch_pool_info(self, address, exchange):
        return self.query_chain.query_unisus_pool(address)  # Replace this later for general one

    def _save_pool(self, info):
        save_path = self.pools_path
        df = self.pools.append(info, ignore_index=True)
        df.to_csv(save_path)

        msg = "New pool saved"
        print(msg.center(70, "*"))
        pprint(info)
        print("*"*70)

    def _get_token_id_and_symbol(self, address):
        # Check if token already exists
        matches = self.tokens[self.tokens.address==address]
        if len(matches) > 1:
            raise Exception(f"More than one token for {address}")
        elif len(matches) == 1:
            return tuple(matches[["id", "symbol"]].iloc[0].to_list())
        # Find the token
        tkn_info = self._fetch_token_info(address)
        # Save it
        last_id = self.tokens["id"].max()
        new_id = "T" + str(int(last_id.lstrip("T"))+1).zfill(4)
        tkn_info["id"] = new_id
        self._save_token(tkn_info)
        return new_id, tkn_info["symbol"]

    def _fetch_token_info(self, address):
        return self.query_chain.query_token(address)

    def _save_token(self, info):
        save_path = self.tokens_path
        df = self.tokens.append(info, ignore_index=True)
        df.to_csv(save_path)

        msg = "New token saved"
        print(msg.center(70, "*"))
        pprint(info)
        print("*"*70)


def main(pool_address, provider, pools_path, tokens_path, exchange=None):
    pa = PoolAdder(pools_path, tokens_path, provider)
    pa.add_pool(pool_address, exchange)


def interactive():
    pool_address = sys.argv[1]
    provider_name = "chainStackAsia"
    pools_path = "./config/pools_test.csv"
    tokens_path = "./config/tokens_test.csv"
    main(pool_address, provider_name, pools_path, tokens_path)


if __name__ == "__main__":
    interactive()


