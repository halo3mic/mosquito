from src.dev_main import Listener
from src.opportunities import EmptySet


avl_opps = [EmptySet]
provider_name = "chainStackBlocklytics"
listener = Listener(provider_name, avl_opps)
# listener.run_time_listener()
listener.run_block_listener()
