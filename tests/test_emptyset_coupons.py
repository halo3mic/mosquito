from src.opportunities import EmptySet
from src.config import provider
from web3 import Web3 




provider_obj = provider("infura")
w3 = Web3(Web3.HTTPProvider(provider_obj.html_path))
es = EmptySet(w3)

response = es.coupons()
print(response)
