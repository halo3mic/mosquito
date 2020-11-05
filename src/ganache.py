import subprocess
import re
import atexit

from src.config import NODE_INFO


# r = requests.post(provider_path, json.dumps({"jsonrpc": "2.0","method": "evm_increaseTime", "params": [100]}))
# r = requests.post(provider_path, json.dumps({"jsonrpc": "2.0","method": "evm_mine", "params": []}))
# requests.post("http://127.0.0.1:8545", json.dumps({"jsonrpc": "2.0","method": "miner_stop", "params": []}))  # Stop Mining
# requests.post("http://127.0.0.1:8545", json.dumps({"jsonrpc": "2.0","method": "miner_start", "params": [2]}))  # Continue mining


def start_ganache(provider, block_number=None, port=8545, mine_interval=None, log=False, unlock=[]):
    private_keys = []
    accounts = []

    mine_interval = "" if not mine_interval else f"-b {mine_interval}"
    # Note that only unsecure ssl connection is supported by ganache - so wss does not work
    provider_prefix = "http://" if provider.startswith("http") else "ws://"
    provider += "@" + str(block_number) if block_number else ""
    unlock_args = []
    for w_address in unlock:
        unlock_args.append("--unlock")
        unlock_args.append(w_address)
    process_args = ["ganache-cli", 
                    *mine_interval, 
                    *unlock_args, 
                    "--callGasLimit", "0x493E0", 
                    "-f", provider, 
                    f"-p {port}", 
                    "-v"]
    try:
        print("Starting ganache ...")
        process = subprocess.Popen(process_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        while 1:
            output = process.stdout.readline().decode("utf-8").strip()
            if output and log: print(output)
            if output.startswith("Error"):
                error = output
                error_msg = error
                while error:
                    error = process.stdout.readline().decode("utf-8")
                    error_msg += "\n" + error
                    if error.endswith("\n"):
                        if not log: break
                raise Exception(error_msg)
            if output.endswith('"evm_mine"'):
                print("#"*80)
                print("  NEW BLOCK MINED  ".center(80, "#"))
                print("#"*80)
            if output.startswith("("):
                if len(accounts) < 10:
                    accounts.append(output.split(" ")[1])
                else:
                    private_keys.append(output.split(" ")[1])
            if output.startswith("Listening on "):
                server_url = provider_prefix + output.split("Listening on ")[1]
                if not log: break

        return process, server_url, accounts, private_keys
    except Exception as e:
        process.kill()
        raise e


if __name__=="__main__":
    node_path = NODE_INFO["alchemy"]["html_path"]
    ganache_process, provider_path, accounts, private_keys = start_ganache(node_path, block_number=10996938, mine_interval=15, log=True)
    atexit.register(lambda: ganache_process.kill())

        

