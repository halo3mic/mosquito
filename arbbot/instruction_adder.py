import src.config as cf
import src.exchanges as ex
import src.helpers as hp
import src.ganache as gc

import pandas as pd
from web3 import Web3
from pprint import pprint
import sys
import time
import atexit


class QueryManager:

    def __init__(self, provider_name="alchemy"):
        self.w3 = cf.web3_api_session(provider_name)
        self.provider_name = provider_name

    def query_unisus_pool(self, pool_address):
        exchange_symbol_dict = {"UNI-V2": "uniswap", "SLP": "sushiswap"}
        fee = 0.003

        pool_address = Web3.toChecksumAddress(pool_address)
        pool_contract = self.w3.eth.contract(address=pool_address, abi=cf.abi("uniswapv2_pool"))
        exchange = pool_contract.functions.symbol().call()
        exchange = exchange_symbol_dict[exchange]
        tkn1 = pool_contract.functions.token0().call()
        tkn2 = pool_contract.functions.token1().call()
        tkns = tkn1, tkn2
        pool_info = {"fee": fee, "tokens": tkns, "address": pool_address, "exchange": exchange}

        return pool_info

    def query_token(self, token_address):
        # Only for ERC20 tokens!
        token_address = Web3.toChecksumAddress(token_address)
        pool_contract = self.w3.eth.contract(address=token_address, abi=cf.abi("erc20_token"))
        symbol = pool_contract.functions.symbol().call()
        decimal = pool_contract.functions.decimals().call()
        token_info = {"symbol": symbol, "decimal": decimal, "address": token_address}
        return token_info

    def query_instruction_gas_cost(self, pool_path, tkn_path):
        # Start ganache
        ganache_session = self.start_ganache(self.provider_name)
        gc_w3 = Web3(Web3.HTTPProvider(ganache_session.node_path))
        avl_exchanges = {"uniswap": ex.Uniswap(gc_w3), "sushiswap": ex.SushiSwap(gc_w3)}
        pool1, pool2 = pool_path
        exchange1 = avl_exchanges[pool1["exchange"]]
        exchange2 = avl_exchanges[pool2["exchange"]]
        sender = ganache_session.accounts[0]
        base_tkn = tkn_path[0]["address"]
        mid_tkn = tkn_path[1]["address"]

        # Approve token for sender
        approve_payload = hp.approve_erc20(mid_tkn, exchange2.router_address)
        hp.execute_payload(gc_w3, approve_payload, sender, gas_price=40, wait4receipt=True)  # Wont work without specifying the gas price
        # Gas for the 1st part of the tx
        args1 = 10**18, (base_tkn, mid_tkn), sender, int(time.time()) 
        # gas_amount1 = self.swapExactETHForTokens_gas(exchange1, *args1)
        execute1_payload = exchange1.swapExactETHForTokens(*args1)
        tx1_receipt = hp.execute_payload(gc_w3, 
                                         execute1_payload, 
                                         sender, 
                                         gas_price=40, 
                                         wait4receipt=True)
        gas_amount1 = tx1_receipt.gasUsed
        # Mid state
        mid_tkn_bal = hp.balance_erc20(gc_w3, sender, mid_tkn)
        # Gas for 2nd part of the tx
        args2 = mid_tkn_bal, (mid_tkn, base_tkn), sender, int(time.time())  
        execute2_payload = exchange2.swapExactTokensForETH(*args2)
        tx2_receipt = hp.execute_payload(gc_w3, 
                                         execute2_payload, 
                                         sender, 
                                         gas_price=40, 
                                         wait4receipt=True)
        gas_amount2 = tx2_receipt.gasUsed
        # All gas
        gas_amount_full = gas_amount1 + gas_amount2

        ganache_session.kill()

        return gas_amount_full
    
    @staticmethod
    def start_ganache(provider_name):
        unlocked = []
        provider = cf.provider(provider_name).html_path
        ganache_session = gc.Ganache(provider, mine_interval=3, unlock=unlocked)
        ganache_session.start_node()
        atexit.register(lambda: ganache_session.kill())  # Closes the node after python session is finished
        return ganache_session


class StorageManager:

    query_mg = QueryManager()

    def __init__(self, name, storage_path, columns=[]):
        self.storage_path = storage_path
        self.columns = columns
        self.df = self._csv2df(storage_path)

    def _csv2df(self, path):
        try:
            return pd.read_csv(path)
        except FileNotFoundError:
            return pd.DataFrame(columns=self.columns)

    def get_by_id(self, id):
        filtered = self.df[self.df.id==id]
        if not len(filtered):
            return 
        elif len(filtered)>1:
            raise Exception(f"More than one row with id {id}")
        return filtered.iloc[0].to_dict()

    def get_by_symbol(self, symbol):
        filtered = self.df[self.df.symbol==symbol]
        if not len(filtered):
            return 
        elif len(filtered)>1:
            raise Exception(f"More than one row with symbol {symbol}")
        return filtered.iloc[0].to_dict()

    def _save(self, data):
        # Check if row already exists by symbol or id
        by_symbol = self.get_by_symbol(data["symbol"])
        if by_symbol:
            raise Exception("Already added!")
        # Generate id for the token
        data["id"] = self._generate_new_id()

        df = self.df.append(data, ignore_index=True)
        df.to_csv(self.storage_path, index=False)
        self.df = df

        msg = "New row saved"
        print(msg.center(70, "*"))
        pprint(data)
        print("*"*70)


    def _generate_new_id(self, add=0):
        new_id = f"X{len(self.df)+1+add:04}"
        if new_id in self.df.id.values:
            return self._generate_new_id(add=add+1)
        return new_id


class TokenManager(StorageManager):

    storage_path = "./config/tokens.csv"
    columns = ["id", "symbol", "address", "decimal", "approved"]

    def __init__(self):
        self.df = self._csv2df(self.storage_path)

    def _generate_new_id(self, add=0):
        new_id = f"T{len(self.df)+1+add:04}"
        if new_id in self.df.id.values:
            return self._generate_new_id(add=add+1)
        return new_id

    def get_by_address(self, address, add_unknown=True):
        filtered = self.df[self.df.address.str.lower()==address.lower()]
        if not len(filtered):
            if add_unknown:
                self.add(address)
                return self.get_by_address(address)
        elif len(filtered)>1:
            raise Exception(f"More than one row with address {address}")
        return filtered.iloc[0].to_dict()

    def add(self, address):
        # info = self.get_by_address(address)
        # if info:
        #     return False
        info = self.query_mg.query_token(address)
        info["approved"] = None
        self._save(info)
        return True


class PoolManager(StorageManager):

    storage_path = "./config/pools.csv"
    columns = ["id", "symbol", "address", "fee", "tokens", "exchange"]

    def __init__(self):
        self.df = self._csv2df(self.storage_path)
        self.token_mg = TokenManager()

    def _generate_new_id(self, add=0):
        new_id = f"P{len(self.df)+1+add:04}"
        if new_id in self.df.id.values:
            return self._generate_new_id(add=add+1)
        return new_id

    def get_by_address(self, address, add_unknown=True):
        filtered = self.df[self.df.address.str.lower()==address.lower()]
        if not len(filtered):
            if add_unknown:
                self.add(address)
                return self.get_by_address(address)
        elif len(filtered)>1:
            raise Exception(f"More than one row with address {address}")
        return filtered.iloc[0].to_dict()

    def add(self, address):
        # info = self.get_by_address(address)
        # if info:
        #     return False
        info = self.query_mg.query_unisus_pool(address)
        tkns = [self.token_mg.get_by_address(a) for a in info["tokens"]]
        info["tokens"] = ", ".join([t["id"] for t in tkns])
        info["symbol"] = ''.join([t["symbol"] for t in tkns]).lower()+"_"+info["exchange"]
        self._save(info)
        return True


class InstructionManager(StorageManager):

    storage_path = "./config/instructions.csv"
    columns = ["id", "symbol", "pool1", "pool2", "path", "gasAmount", "enabled"]

    def __init__(self):
        self.df = self._csv2df(self.storage_path)
        self.pool_mg = PoolManager()

    def _generate_new_id(self, add=0):
        new_id = f"I{len(self.df)+1+add:04}"
        if new_id in self.df.id.values:
            return self._generate_new_id(add=add+1)
        return new_id

    def add(self, pools):
        # Obtain pool and token information
        pool_info = [self.pool_mg.get_by_address(p) for p in pools]
        tkn_pairs = [set(p["tokens"]) for p in pool_info]
        # Sort tkns in order of execution
        # NOTE Now only eth-->tkn-->eth supported
        if tkn_pairs[0] != tkn_pairs[1]:
            raise Exception("Tokens pairs dont have the same tokens")
        tkn_ids = set(t for p in pool_info for t in p["tokens"].split(", "))
        base_tkn_symbol = "WETH"
        base_tkn = self.pool_mg.token_mg.get_by_symbol(base_tkn_symbol)["id"]
        tkn_ids.remove(base_tkn)
        if not tkn_ids:
            raise Exception("Corrupted path")
        mid_tkn = tkn_ids.pop()
        tkn_path = (base_tkn, mid_tkn, base_tkn)
        tkn_path_str = ", ".join(tkn_path)
        # Generate instruction symbol
        tkn_info = [self.pool_mg.token_mg.get_by_id(t) for t in tkn_path]
        tkn_symbols = [t["symbol"] for t in tkn_info]
        exchanges = [p["exchange"] for p in pool_info]
        instr_symbol = ("2".join(tkn_symbols) + "_" + "2".join(exchanges)).lower()
        # Estimate gas
        gas_amount = self.query_mg.query_instruction_gas_cost(pool_info, tkn_info)
        info = {"symbol": instr_symbol, 
                "pool1": pool_info[0]["id"], 
                "pool2": pool_info[1]["id"], 
                "path": tkn_path_str, 
                "gasAmount": gas_amount, 
                "enabled": 1}
        self._save(info)
        return True


def add_from_table(table_path=None):
    default_path = "./config/instr2beAdded.csv"
    table_path = table_path if table_path else default_path

    InstructionManager.storage_path = "./config/instructions_test.csv"
    PoolManager.storage_path = "./config/pools_test.csv"
    TokenManager.storage_path = "./config/tokens_test.csv"
    instr_mg = InstructionManager()

    request_df = pd.read_csv(table_path)
    for index, row in request_df.iterrows():
        if not row.added:
            try:
                pool_pairs = row.pool1Address, row.pool2Address
                # Add the instruction
                print(f"Adding instruction: {row.pool1Name}<>{row.pool2Name}")
                instr_mg.add(pool_pairs)
                if row.reverse:
                    print(f"Adding instruction: {row.pool2Name}<>{row.pool2Name}")
                    instr_mg.add(pool_pairs[::-1])
                # Change added to True
                request_df.at[index, "added"] = True
            except Exception as e:
                print(repr(e))
            finally:
                # Save the state of the dataframe
                request_df.to_csv(table_path, index=False)


if __name__=="__main__":
    add_from_table()