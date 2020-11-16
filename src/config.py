import json
from dotenv import dotenv_values
from web3 import Web3
import os

_INTERNAL_STORAGE = {}
_env_vals = dotenv_values("./config/.env")

BOT_ID = "MSQT1"
RESULT_LOG_PATH = "./logs/stats.csv"

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
                 "ethnme": "0xddbE1dFC668233bb882014838DAE50deF5Ea967c", 
                 "usdcesd": "0x88ff79eB2Bc5850F27315415da8685282C7610F9", 
                 "ethusdc": "0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc"
                 },
             "supplierAddress": "0xCFb13c3248887Ab43d1777b63E57a84e8250A033", 
             "dispatcher_address": "0xF451b59d6db7A6601B15d6250624db7329867bae",
             "tokens": {"weth9": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2", 
                        "nme": "0x404A03728Afd06fB934e4b6f0EaF67796912733A", 
                        "esd": "0x36F3FD68E7325a35EB768F1AedaAe9EA0689d723", 
                        "usdc": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48", 
                        "dai": "0x6B175474E89094C44Da98b954EedeAC495271d0F"
                        }
            }
TKN_DECIMALS = {"esd": 18, 
                "nme": 18, 
                "weth9": 18, 
                "usdc": 9, 
                "dai": 18
                }

# # ABIS
# abi_contracts = ["0x404A03728Afd06fB934e4b6f0EaF67796912733A", 
#                  "uniswapv2", 
#                  "uniswapv2_router02", 
#                  "erc20_token", 
#                  "0xdAf2593AaF8EF040E279c806aaB8deDFE534d421"]
# ABIS = {}
# for name in abi_contracts:
#     path = f"./abis/{name}.json"
#     ABIS[name] = json.dumps(json.load(open(path)))

# NODE
NODE_INFO = {"infura": {
                "html_path": "https://mainnet.infura.io/v3/<<TOKEN>>",
                "ws_path": "wss://mainnet.infura.io/ws/v3/<<TOKEN>>",  
                "ws_blocks_request": '{"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}'
             },
             "alchemy": {
                 "html_path": "https://eth-mainnet.alchemyapi.io/v2/<<TOKEN>>",
                 "ws_path": "wss://eth-mainnet.ws.alchemyapi.io/v2/<<TOKEN>>", 
                 "ws_blocks_request": '{"jsonrpc":"2.0","id": 1, "method": "eth_subscribe", "params": ["newHeads"]}'
             },
             "quickNode": {
                 "html_path": "https://crimson-holy-water.quiknode.pro/<<TOKEN>>",
                 "ws_path": "wss://crimson-holy-water.quiknode.pro/<<TOKEN>>", 
                 "ws_blocks_request": '{"jsonrpc":"2.0","id": 1, "method": "eth_subscribe", "params": ["newHeads"]}'
             }, 
             "localNode": {
                 "html_path": "http://localhost:7777", 
                 "ws_path": "ws://localhost:7778", 
                 "ws_blocks_request": '{"jsonrpc":"2.0","id": 1, "method": "eth_subscribe", "params": ["newHeads"]}'
             },
             "chainStack": {
                 "html_path": "https://youthful-goodall:<<TOKEN>>@nd-018-495-294.p2pify.com", 
                 "ws_path": "wss://youthful-goodall:<<TOKEN>>@ws-nd-018-495-294.p2pify.com", 
                 "ws_blocks_request": '{"jsonrpc":"2.0","id": 1, "method": "eth_subscribe", "params": ["newHeads"]}'
             }
            }


def _fetch_abis():
    abis_dict = {}
    folder_path = "./config/abis"
    elements = os.listdir(folder_path)
    for e in elements:
        path = f"{folder_path}/{e}"
        abi_name = e.split(".json")[0]
        abis_dict[abi_name] = json.dumps(json.load(open(path)))

    _INTERNAL_STORAGE["abis"] = abis_dict


def abis(abi_name):
    return _INTERNAL_STORAGE["abis"].get(abi_name)


_fetch_abis()

