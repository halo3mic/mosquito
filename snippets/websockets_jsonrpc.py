from web3 import Web3
import src.config as cf
import src.helpers as hp
import src.exchanges as ex


provider_name = "chainStackUsa"
provider_obj = cf.provider(provider_name)
w3 = Web3(Web3.WebsocketProvider(provider_obj.ws_path, websocket_timeout=60))

uniswap = ex.Uniswap(w3)
print(w3.eth.blockNumber)
print(w3.eth.getBalance(cf.address("msqt_dispatcher")))
print(uniswap.get_reserves("0x48A91882552Dad988AE758fCb7070B8E9844DeC5"))