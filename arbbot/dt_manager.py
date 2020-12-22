import pandas as pd 
from collections import namedtuple as nt
from pprint import pprint


def rows2namedtuples(name, data):
    nt_class = nt(name, data.keys())
    dics = [{key : value[k] for key, value in data.items()} for k in data["id"].keys()] 
    instances = dict((row["id"], nt_class(**row)) for row in dics)
    return instances


def fetch_data(path, fltr=None):

    def apply_filter(df):
        for key, val in fltr.items():
            df = df[df[key].isin(val)] 
        return df

    df = pd.DataFrame(pd.read_csv(path))
    if fltr:
        df = apply_filter(df)
    return df.to_dict()


def deserialize(fltr=None):
    tkns_path = "./config/tokens.csv"
    pools_path = "./config/pools.csv"
    atomic_path = "./config/atomic_opps.csv"

    # Fetch and seralize all the tokens
    tkn_dict = fetch_data(tkns_path)
    tkns = rows2namedtuples("Token", tkn_dict)

    # Fetch all pools
    pool_dict = fetch_data(pools_path)
    # In pools replace token strings with token objects
    for i in range(len(pool_dict["id"])):
        pool_tkn_ids = pool_dict["tokens"][i].split(", ")
        pool_dict["tokens"][i] = [tkns[tkn_id] for tkn_id in pool_tkn_ids]
    # Seralize the pools
    pools = rows2namedtuples("Pool", pool_dict)

    # Fetch the atomic pairs based on the filter
    atm_dict = fetch_data(atomic_path, fltr=fltr)
    # In pools replace pool strings with pool objects
    for k in atm_dict["id"].keys():
        atm_dict["pool1"][k] = pools[atm_dict["pool1"][k]]
        atm_dict["pool2"][k] = pools[atm_dict["pool2"][k]]
    atm_opps = rows2namedtuples("AtmOpp", atm_dict)

    return atm_opps


def get_atm_opps(select=None):
    selection = {"symbol": select} if select else None
    atm_opps = deserialize(fltr=selection)
    formatted = list(atm_opps.values())
    return formatted


if __name__ == "__main__":
    # symbol_filter = {"symbol": ["wbtcweth_ssuni", "linkweth_ssuni", "amplweth_ssuni"]}
    # atm_opps = deserialize(fltr=symbol_filter)
    # pprint(atm_opps)
    # dic = fetch_data("./config/tokens.csv")
    # dics = [{key : value[i] for key, value in dic.items()} for i in range(len(dic["id"]))] 
    # instances = rows2namedtuples("Test", dic)
    pprint(get_atm_opps(select=["amplweth_ssuni"]))