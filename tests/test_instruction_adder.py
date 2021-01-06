from arbbot import instruction_adder as ia

from pprint import pprint


def test_token_manager():
    tkn_mg = ia.TokenManager()
    # Get token info
    tkn_id = "T0001"
    tkn_symbol = "WETH"
    tkn_info_from_id = tkn_mg.get_by_id(tkn_id)
    tkn_info_from_symbol = tkn_mg.get_by_symbol(tkn_symbol)
    assert tkn_info_from_id["symbol"] == tkn_symbol
    assert tkn_info_from_symbol["id"] == tkn_id
    # New id
    df = tkn_mg.df
    new_df = df.drop(df.loc[df.id==tkn_id].index, axis=0)
    tkn_mg.df = new_df
    new_id = tkn_mg._generate_new_id()
    assert df.id.iloc[-1] != new_id
    # Add new token
    tkn_mg.storage_path = "./config/tokens_test.csv"
    address = "0x1f3f9d3068568f8040775be2e8c03c103c61f3af"
    symbol = "ARCH"
    tkn_mg.add(address)
    added_tkn = tkn_mg.get_by_address(address)
    assert added_tkn["symbol"] == symbol


def test_pool_manager():
    pool_mg = ia.PoolManager()
    # Get token info
    pool_id = "P0003"
    pool_symbol = "linkweth_uniswap"
    pool_info_from_id = pool_mg.get_by_id(pool_id)
    pool_info_from_symbol = pool_mg.get_by_symbol(pool_symbol)
    assert pool_info_from_id["symbol"] == pool_symbol
    assert pool_info_from_symbol["id"] == pool_id
    # New id
    df = pool_mg.df
    new_df = df.drop(df.loc[df.id==pool_id].index, axis=0)
    pool_mg.df = new_df
    new_id = pool_mg._generate_new_id()
    assert df.id.iloc[-1] != new_id
    # Add new token
    pool_mg.storage_path = "./config/pools_test.csv"
    pool_mg.token_mg.storage_path = "./config/tokens_test.csv"
    address = "0xd3d2e2692501a5c9ca623199d38826e513033a17"
    symbol = "uniweth_uniswap"
    pool_mg.add(address)
    added_tkn = pool_mg.get_by_address(address)
    assert added_tkn["symbol"] == symbol


def test_instruction_manager():
    instr_mg = ia.InstructionManager()
    # Get token info
    instr_id = "I0003"
    instr_symbol = "weth2link2weth_uniswap2Sushiswap"
    instr_info_from_id = instr_mg.get_by_id(instr_id)
    instr_info_from_symbol = instr_mg.get_by_symbol(instr_symbol)
    assert instr_info_from_id["symbol"] == instr_symbol
    assert instr_info_from_symbol["id"] == instr_id
    # New id
    df = instr_mg.df
    new_df = df.drop(df.loc[df.id==instr_id].index, axis=0)
    instr_mg.df = new_df
    new_id = instr_mg._generate_new_id()
    assert df.id.iloc[-1] != new_id
    # Add new token
    instr_mg.storage_path = "./config/instructions_test.csv"
    instr_mg.pool_mg.storage_path = "./config/pools_test.csv"
    instr_mg.pool_mg.token_mg.storage_path = "./config/tokens_test.csv"
    pools = ("0xd3d2e2692501a5c9ca623199d38826e513033a17", "0xdafd66636e2561b0284edde37e42d192f2844d40")
    symbol = "weth2uni2weth_uniswap2sushiswap"
    instr_mg.add(pools)
    added_tkn = instr_mg.get_by_symbol(symbol)


def test_instruction_adding():
    pool_pairs = [("0xd3d2e2692501a5c9ca623199d38826e513033a17", 
                   "0xdafd66636e2561b0284edde37e42d192f2844d40")]
    ia.InstructionManager.storage_path = "./config/instructions_test.csv"
    ia.PoolManager.storage_path = "./config/pools_test.csv"
    ia.TokenManager.storage_path = "./config/tokens_test.csv"
    instr_mg = ia.InstructionManager()
    for pp in pool_pairs:
        instr_mg.add(pp)

if __name__=="__main__":
    test_instruction_adding()
    # test_instruction_manager()