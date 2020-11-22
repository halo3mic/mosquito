from src.opportunities import EmptySet
from src.config import provider
from web3 import Web3 


infura = provider("infura")
w3 = Web3(Web3.HTTPProvider(infura.html_path))
es = EmptySet(w3)

# Too soon for opportunity 
es.last_opp_block = 0
es.web3.blockNumber = 200
es.nextEpochTimestamp = 57600
block_timestamp = 57600-16
assert not es.is_epoch(block_timestamp)

# Opportunity found
es.last_opp_block = 0
es.web3.blockNumber = 200
es.nextEpochTimestamp = 57600
block_timestamp = 57600-15
assert es.is_epoch(block_timestamp)

# Opportunity found in the same block
es.last_opp_block = 200
es.web3.blockNumber = 200
es.nextEpochTimestamp = 57600
block_timestamp = 57600-15
assert not es.is_epoch(block_timestamp)

# Update epoch if opportunity detected and was also detected in the last 10 blocks
## Opportunity was taken
es._get_epoch = lambda: es.calc_epochTime(57600*2)-1
es.last_opp_block = 191
es.web3.blockNumber = 200
es.nextEpochTimestamp = 57600
block_timestamp = 57600-15
assert not es.is_epoch(block_timestamp)
## Opportunity is still available
es._get_epoch = lambda: es.calc_epochTime(57600)-1
es.last_opp_block = 191
es.web3.blockNumber = 200
es.nextEpochTimestamp = 57600
block_timestamp = 57600-15
assert es.is_epoch(block_timestamp)

# Update epoch if opportunity detected and targetTime < currentTime
## Opportunity was taken
es._get_epoch = lambda: es.calc_epochTime(57600*2)-1
es.last_opp_block = 191
es.web3.blockNumber = 200
es.nextEpochTimestamp = 57600
block_timestamp = 57600+15
assert not es.is_epoch(block_timestamp)
## Opportunity is still available
es._get_epoch = lambda: es.calc_epochTime(57600)-1
es.last_opp_block = 191
es.web3.blockNumber = 200
es.nextEpochTimestamp = 57600
block_timestamp = 57600+15
assert es.is_epoch(block_timestamp)