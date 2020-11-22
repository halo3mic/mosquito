from src import ganache as gn
from src.dev_main import Listener
from src.opportunities import EmptySet
import src.config as cf


target_block = "11304643"
provider_name = "chainStackAsia"
provider_obj = cf.provider(provider_name)
start_block_number = target_block-3
ganache_session = Ganache(provider_obj.html_path, block_number=start_block_number, mine_interval=None)
ganache_session.start_node()
atexit.register(lambda: ganache_session.kill())  # Closes the node after python session is finished
ganache_html = ganache_session.node_path
ganache_node = provider_obj.copy()
ganache_node.html_path = ganache_html


avl_opps = [EmptySet]
listener = Listener(provider_name, avl_opps)
listener.provider = ganache_node
# listener.run_time_listener()
listener.run_block_listener()