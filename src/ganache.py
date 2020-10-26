import subprocess
import re
import atexit

from config import NODE_INFO


def start_ganache(provider, block_number=None, port=8545, mine_interval=None, log=False):
    private_keys = []
    accounts = []

    mine_interval = "" if not mine_interval else f"-b {mine_interval}"
    # Note that only unsecure ssl connection is supported by ganache - so wss does not work
    provider_prefix = "http://" if provider.startswith("http") else "ws://"
    provider += "@" + str(block_number) if block_number else ""
    unlock = "0x2493336E00A8aDFc0eEDD18961A49F2ACAf8793f"
    try:
        print("Starting ganache ...")
        process = subprocess.Popen(["ganache-cli", mine_interval, "--unlock", unlock, "--callGasLimit",  "0x493E0", "-f", provider, f"-p {port}", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

        

