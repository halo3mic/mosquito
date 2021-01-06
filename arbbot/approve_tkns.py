from src import gas_manager as gm
from src import helpers as hp
from src import config as cf

import pandas as pd
import numpy as np


def approve_archer_tkns(w3, dispatcher_address, tkns, spender, approver_address, gas_cost_threshold=0.1):
    dispatcher = w3.eth.contract(abi=cf.abi("dispatcher"), address=dispatcher_address)
    gas_price = gm.fetch_gas_price()["standard"]
    approver_pk = cf.private_key(approver_address)

    not_approved_before = tokens_not_approved(w3, tkns, dispatcher_address, spender)
    print(not_approved_before)
    # fun_call = dispatcher.functions.tokenAllowAll(not_approved_before, spender)
    # tx = fun_call.buildTransaction({"from": approver_address, 
    #                                 "nonce": w3.eth.getTransactionCount(approver_address)})
    # gas_amount = w3.eth.estimateGas(tx)
    # if gas_amount*gas_price/10**18 > gas_cost_threshold:
    #     raise Exception("Gas cost too big")
    # sig_tx = w3.eth.account.sign_transaction(tx, private_key=approver_pk)
    # tx_hash = w3.eth.sendRawTransaction(sig_tx.rawTransaction).hex()
    # print(f"Pending tx at: {tx_hash}")
    # r = w3.eth.waitForTransactionReceipt(tx_hash, timeout=600)
    # not_approved_after = tokens_not_approved(w3, not_approved_before, dispatcher_address, spender)
    # if r.status == 0 or not_approved_after:
    #     raise Exception("Approval failed")
        

def tokens_not_approved(w3, tkns, dispatcher_address, spender_address):
    not_approved = []
    for t in tkns:
        approved_amount = hp.erc20_approved(w3, t, dispatcher_address, spender_address)
        if approved_amount==0:
            not_approved.append(t)

    return not_approved


def str2tuple(request):
    tpl = request.strip("()").split(",")
    tpl = tuple(e.strip() for e in tpl)
    return tpl


def tuple2str(tpl):
    return ", ".join(tpl).strip("()")


def approve_tkns(provider="infura"):
    w3 = cf.web3_api_session(provider)
    approver_address = cf.address("msqt_worker")
    dispatcher_address = cf.address("msqt_dispatcher")
    tkns_storage_path = "./config/tokens_test.csv"
    tkn_df = pd.read_csv(tkns_storage_path)
    spenders = [cf.address("uniswapv2_router"), cf.address("sushiswap_router")]
    tkn_df.approved = tkn_df.approved.apply(lambda x: str2tuple(x) if x!="None" else tuple())
    try:
        for spender in spenders:
            not_approved = tkn_df.loc[~tkn_df["approved"].str.contains(spender, regex=False)].address.to_list()
            not_approved_str = '\n\t'.join(not_approved).strip('()')
            print("")
            print(f"Approving\n\t{not_approved_str}\nfor spender {spender}")
            
            approve_archer_tkns(w3, dispatcher_address, not_approved, spender, approver_address)
            fltr = lambda x: tuple(x.approved+(spender, )) if x.address in not_approved else x.approved
            tkn_df.approved = tkn_df.apply(fltr, axis=1)
    except Exception as e:
        # print(repr(e))
        raise e
    finally:
        tkn_df.approved = tkn_df.approved.apply(lambda x: tuple2str(x))
        tkn_df.to_csv(tkns_storage_path, index=False)


if __name__ == "__main__":
    approve_tkns()
    
