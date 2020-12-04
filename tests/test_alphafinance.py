from src.opportunities import AlphaFinance
from src.config import provider
from web3 import Web3 


provider_obj = provider("infura")
w3 = Web3(Web3.HTTPProvider(provider_obj.html_path))
af = AlphaFinance(w3)

response = af.get_all_goblins()
print(response)
