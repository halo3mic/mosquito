import os
import json
from web3 import Web3
from dotenv import dotenv_values
from types import SimpleNamespace


def _fetch_abis():
    abis_dict = {}
    folder_path = "./config/abis"
    elements = os.listdir(folder_path)
    for e in elements:
        path = f"{folder_path}/{e}"
        abi_name = e.split(".json")[0]
        abis_dict[abi_name] = json.dumps(json.load(open(path)))

    _INTERNAL_STORAGE["abis"] = abis_dict


def _fetch_providers():
    path = "./config/providers.json"
    providers_raw = json.load(open(path))
    providers = providers_raw.copy()
    for key, value in providers_raw.items():
        providers[key]["ws_blocks_request"] = json.dumps(providers_raw[key]["ws_blocks_request"])
        for ikey, ival in value.items():
            if "<<TOKEN>>" in ival:
                keyword = key.upper() + "_TOKEN"
                secret = _ENV_VALS.get(keyword)
                if not secret:
                    break
                providers[key][ikey] = ival.replace("<<TOKEN>>", secret)
    _INTERNAL_STORAGE["providers"] = providers


def _fetch_addresses():
    path = "./config/addresses.json"
    _INTERNAL_STORAGE["addresses"] = json.load(open(path))


def abi(abi_name):
    return _INTERNAL_STORAGE["abis"].get(abi_name)


def provider(provider_name):
    provider_obj = SimpleNamespace(**_INTERNAL_STORAGE["providers"].get(provider_name))
    provider_obj.name = provider_name
    return provider_obj


def address(address_key):
    return _INTERNAL_STORAGE["addresses"].get(address_key)

def private_key(address):
    try:
        key = "PK_"+address
        return _ENV_VALS[key]
    except KeyError:
        raise Exception(f"Private key for {address} not found")


def web3_api_session(provider_name):
    provider_address = provider(provider_name).html_path
    return Web3(Web3.HTTPProvider(provider_address))


# Load variables
_INTERNAL_STORAGE = {}
_ENV_VALS = dotenv_values("./config/.env")
_fetch_abis()
_fetch_providers()
_fetch_addresses()
# bot_id = "MSQT1"
bot_id = "2"
archer_api_key = _ENV_VALS["ARCHER_API_TOKEN"]
archer_api_endpoint = "http://127.0.0.1:5000/submit"
save_logs_path = "./logs/stats.csv"
tkn_dec = {"esd": 18, 
           "nme": 18, 
           "weth9": 18, 
           "usdc": 9, 
           "dai": 18}


