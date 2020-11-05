import json
from dotenv import dotenv_values
from web3 import Web3

_env_vals = dotenv_values("./.env")

# ADDRESSES
ADDRESSES = {"halfrekt": 
                {"exploiter": "0x223034EDbe95823c1160C16F26E3000315171cA9", 
                 "halfrekt": "0x404A03728Afd06fB934e4b6f0EaF67796912733A"
                 }, 
             "emptyset":
                {"implementation": "0xdAf2593AaF8EF040E279c806aaB8deDFE534d421", 
                 "proxy": "0x443D2f2755DB5942601fa062Cc248aAA153313D3"
                 },
             "uniswap": 
                 {"uniswapv2_router02": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D", 
                 "ethnme": "0xddbE1dFC668233bb882014838DAE50deF5Ea967c"
                 },
             "tokens": {"weth9": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 
                        "nme": "0x404A03728Afd06fB934e4b6f0EaF67796912733A", 
                        "esd": "0x36F3FD68E7325a35EB768F1AedaAe9EA0689d723", 
                        "usdc": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
                        }
            }

# ABIS
abi_contracts = ["0x404A03728Afd06fB934e4b6f0EaF67796912733A", 
                 "uniswapv2", 
                 "uniswapv2_router02", 
                 "erc20_token", 
                 "0xdAf2593AaF8EF040E279c806aaB8deDFE534d421"]
ABIS = {}
for name in abi_contracts:
    path = f"./abis/{name}.json"
    ABIS[name] = json.dumps(json.load(open(path)))

# NODE
NODE_INFO = {"infura": {
                "html_path": f"https://mainnet.infura.io/v3/{_env_vals['INFURA_TOKEN']}",
                "ws_path": f"wss://mainnet.infura.io/ws/v3/{_env_vals['INFURA_TOKEN']}",  
                "ws_blocks_request": '{"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}'
             },
             "alchemy": {
                 "html_path": f"https://eth-mainnet.alchemyapi.io/v2/{_env_vals['ALCHEMY_TOKEN']}",
                 "ws_path": f"wss://eth-mainnet.ws.alchemyapi.io/v2/{_env_vals['ALCHEMY_TOKEN']}", 
                 "ws_blocks_request": '{"jsonrpc":"2.0","id": 1, "method": "eth_subscribe", "params": ["newHeads"]}'
             }
            }

# WALLETS
# WALLETS = {"Test account": (_env_vals['ADDRESS'], _env_vals['PRIVATE_KEY'])}

# INSTANCE STORAGE
STORAGE = {}
