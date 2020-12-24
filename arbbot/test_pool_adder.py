from arbbot.pool_adder import QueryChain, PoolAdder
from pprint import pprint


def test_pool_query():
    provider_name = "chainStackAsia"
    # exchange = "SushiSwap"
    injweth_address = "0xFb3cD0B8A5371fe93ef92E3988D30Df7931E2820"
    q = QueryChain(provider_name)
    # result1 = q.query_pool(injweth_address, exchange)
    result2 = q.query_unisus_pool(injweth_address)
    # assert result1 == result2
    pprint(result2)


def test_token_query():
    provider_name = "chainStackAsia"
    inj_address = "0xe28b3B32B6c345A34Ff64674606124Dd5Aceca30"
    q = QueryChain(provider_name)
    result = q.query_token(inj_address)
    pprint(result)


def test_pool_adder():
    provider_name = "chainStackAsia"
    exchange = "SushiSwap"
    injweth_address = "0xFb3cD0B8A5371fe93ef92E3988D30Df7931E2820".lower()
    pools_path = "./config/pools.csv"
    tokens_path = "./config/tokens.csv"
    pa = PoolAdder(pools_path, tokens_path, provider_name)
    pa.add_pool(injweth_address, exchange)


if __name__ == "__main__":
    # test_pool_query()
    # test_token_query()
    test_pool_adder()
    