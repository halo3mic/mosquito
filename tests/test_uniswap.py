    # uni = Uniswap(w3)
    # dai_address = "0x6B175474E89094C44Da98b954EedeAC495271d0F"
    # path = [dai_address, "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"]
    # pool_address = "0xA478c2975Ab1Ea89e8196811F51A7B7Ade33eB11"
    # dai_amount = 300
    # dai_contract = w3.eth.contract(address=dai_address, abi=ABIS["erc20_token"])
    
    # # print("#"*80)
    # # payload_transfer = transfer_erc20(dai_address, wallet_address2, 300*10**18)
    # # tx_hash = execute(payload_transfer)
    # # tx_reciept = w3.eth.waitForTransactionReceipt(tx_hash)
    # # pprint(tx_reciept)
    # # wallet_address = wallet_address2
    # # print(dai_contract.functions.balanceOf(wallet_address).call()/10**18)
    # # print("#"*80)
    # payload_approve = approve_erc20(dai_address, "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D", amount=400*10**18)
    # # pprint(payload_approve)
    # tx_hash = execute(payload_approve)
    # # tx_reciept = w3.eth.waitForTransactionReceipt(tx_hash)
    # # pprint(tx_reciept)
    # # allowance = dai_contract.functions.allowance(wallet_address, "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D").call()/10**18
    # # print(allowance)
    # # if not allowance: exit()
    # print(dai_contract.functions.balanceOf(wallet_address).call()/10**18)
    # bal_eth1 = w3.eth.getBalance(wallet_address)
    # # print(bal_eth1)
    # # print("#"*80)
    # eth_out = uni.get_amount_out(dai_amount, pool_address, inverse=1)
    # print(eth_out/10**18)
    # trade_payload = uni.get_payload(300*10**18, 
    #                                  eth_out*10**18, 
    #                                  path, 
    #                                  400000, 
    #                                  wallet_address)
    # pprint(trade_payload)
    # tx_hash = execute(trade_payload)
    # tx_reciept = w3.eth.waitForTransactionReceipt(tx_hash)
    # # pprint(tx_reciept)
    # bal_eth2 = w3.eth.getBalance(wallet_address)
    # # print(bal_eth2)
    # print("profit:", bal_eth2-bal_eth1)

    # balance_nme = halfrekt_contract.functions.balanceOf(wallet_address).call()
    # tx_reciept3 = execute(response["payloads"][2])