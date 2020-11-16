# HELPERS

provider = NODE_INFO["infura"]["html_path"]
w3 = Web3(Web3.HTTPProvider(provider))

input_amount = 4000
to_address = "0xddbE1dFC668233bb882014838DAE50deF5Ea967c"
pool_address = "0xddbE1dFC668233bb882014838DAE50deF5Ea967c"
path = ["0x404A03728Afd06fB934e4b6f0EaF67796912733A", "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"]

uni = Uniswap(w3)
amount_out = uni.get_amount_out(input_amount, pool_address, inverse=1)
payload = uni.get_payload(input_amount, amount_out, path, 200000, to_address)

print(amount_out)
print(payload)

payload = approve_erc20("0x3f382dbd960e3a9bbceae22651e88158d2791550", "0x93eA6ec350Ace7473f7694D43dEC2726a515E31A", 1000000000000000000000000000)
print(payload)

transfer_result = "0xa9059cbb000000000000000000000000ec0b879271e4009230427d02a057b595735b2bf9000000000000000000000000000000000000000000000015af1d78b58c400000"
assert transfer_result == transfer_erc20("0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984", "0xEC0B879271e4009230427d02A057B595735b2Bf9", 400*10**18)["calldata"]


# 