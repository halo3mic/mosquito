from src.listener import Listener, OpportunityManager
from arbbot.main import ArbBot


avl_opps = [ArbBot]
api_provider_name = "chainStackBlocklytics"
ws_provider_name = "chainStackBlocklytics"
opp_manager = OpportunityManager(avl_opps, api_provider_name)
listener = Listener(ws_provider_name, opp_manager)
listener.run_block_listener()