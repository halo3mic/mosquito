from src.listener import Listener
from arbbot.main import ArbBot


avl_opps = [ArbBot]
provider_name = "chainStackBlocklytics"
listener = Listener(provider_name, avl_opps)
listener.run_block_listener()