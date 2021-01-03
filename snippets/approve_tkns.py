from src import config as cf
from src import helpers as hp
from src import gas_manager as gm

import pandas as pd


def approve_archer_tkns(w3, dispatcher_address, tkns, spenders, approver_address, gas_cost_threshold=0.1):
    dispatcher = w3.eth.contract(abi=cf.abi("dispatcher"), address=dispatcher_address)
    gas_price = gm.fetch_gas_price()["standard"]
    approver_pk = cf.private_key(approver_address)
    for spender in spenders:
        tx = dispatcher.functions.tokenAllowAll(tkns, spender).buildTransaction({"from": approver_address, "nonce": w3.eth.getTransactionCount(approver_address)})
        gas_amount = w3.eth.estimateGas(tx)
        print(gas_amount, gas_price, gas_amount*gas_price/10**18)
        if gas_amount*gas_price/10**18 > gas_cost_threshold:
            raise Exception("Gas cost too big")
        # sig_tx = w3.eth.account.sign_transaction(tx, private_key=approver_pk)
        # tx_hash = w3.eth.sendRawTransaction(sig_tx.rawTransaction).hex()
        # print(f"Pending tx at: {tx_hash}")
        # r = w3.eth.waitForTransactionReceipt(tx_hash, timeout=600)
        if r.status == 0:
            raise Exception("Approval failed")
        for t in tkns:
            approved_amount = hp.erc20_approved(w3, t, dispatcher.address, spender, convert=1)
            print(f"Router can now take {approved_amount} tokens ({t}) from dispatcher")


def default_approve(tkns, provider="infura"):
    w3 = cf.web3_api_session(provider)
    dispatcher_address = cf.address("msqt_dispatcher")
    spenders = [cf.address("uniswapv2_router"), cf.address("sushiswap_router")]
    approver_address = cf.address("msqt_worker")
    approve_archer_tkns(w3, dispatcher_address, tkns, spenders, approver_address)


def get_all_tkns():
    tkn_df = pd.read_csv("./config/tokens.csv")
    return tkn_df.address.to_list()


# if __name__ == "__main__":
#     tkn_addresses = get_all_tkns()
#     default_approve(tkn_addresses)

