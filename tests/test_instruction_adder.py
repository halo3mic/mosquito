from arbbot import instruction_adder as ia


def test_token_manager():
    tkn_id = "T0001"
    tkn_symbol = "WETH"
    tkn_mg = ia.TokenManager()

    # Get token info
    tkn_info_from_id = tkn_mg.get_tkn_by_id(tkn_id)
    tkn_info_from_symbol = tkn_mg.get_tkn_by_symbol(tkn_symbol)
    assert tkn_info_from_id["symbol"] == tkn_symbol
    assert tkn_info_from_symbol["symbol"] == tkn_id
    
    # New id
    new_id = tkn_mg._generate_new_id()
    assert len(tkn_mg.tkn_df)+1 == new_id






if __name__=="__main__":
    test_token_manager()