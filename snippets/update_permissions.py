from src import config as cf
from src import helpers as hp
from src import gas_manager as gm


def lose_privilage(w3, dispatcher_address, role, updater, gas_cost_threshold=0.03):
    dispatcher = w3.eth.contract(abi=cf.abi("dispatcher"), address=dispatcher_address)
    has_role = dispatcher.functions.hasRole(role, updater).call()
    role_count = dispatcher.functions.getRoleMemberCount(role).call()
    print(f"Account {updater} has role {role}: {has_role}")
    print(f"{role_count} accounts have role {role}")
    # if has_role:
    #     tx = dispatcher.functions.renounceRole(role, updater).buildTransaction({"from": updater, "nonce": w3.eth.getTransactionCount(updater)})
    #     updater_pk = cf.private_key(updater)
    #     gas_amount = w3.eth.estimateGas(tx)
    #     gas_price = gm.fetch_gas_price()["standard"]
    #     print(gas_amount, gas_price, gas_amount*gas_price/10**18)
    #     if gas_amount*gas_price/10**18 > gas_cost_threshold:
    #         raise Exception("Gas cost too big")

    #     sig_tx = w3.eth.account.sign_transaction(tx, private_key=updater_pk)
    #     tx_hash = w3.eth.sendRawTransaction(sig_tx.rawTransaction).hex()
    #     print(f"Pending tx at: {tx_hash}")
    #     r = w3.eth.waitForTransactionReceipt(tx_hash, timeout=600)

    #     has_role = dispatcher.functions.hasRole(role, updater).call()
    #     print(f"Account {updater} has role {role}: {has_role}")
    #     if r.status == 0 or has_role:
    #         raise Exception("Approval failed")


def default(provider="infura"):
    role = "ea728681f55b7658af02b019305006d1b2faefced46ff12facedd896da3c3dc6"  # WHITELISTED_LP_ROLE
    w3 = cf.web3_api_session(provider)
    dispatcher_address = cf.address("msqt_dispatcher")
    updater = cf.address("msqt_worker")
    lose_privilage(w3, dispatcher_address, role, updater)


if __name__=="__main__":
    default()