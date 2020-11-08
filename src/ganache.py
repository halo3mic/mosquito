import subprocess
import requests
import json
import re


class Ganache:

    def __init__(self, provider, block_number=None, port=8545, mine_interval=None, unlock=[]):
        provider_prefix = "http://" if provider.startswith("http") else "ws://"  # wss does not work
        self.provider_suffix = ("@" + str(block_number)) if block_number else ""
        self.provider = provider
        self.port = port
        self.mine_interval = "" if not mine_interval else f"-b {mine_interval}"
        self.node_path = provider_prefix + "127.0.0.1:" + str(port)
        self.unlock_args = []
        for w_address in unlock:
            self.unlock_args.append("--unlock")
            self.unlock_args.append(w_address)
        self.process = None

    def start_node(self):
        process_args = ["ganache-cli", 
                        self.mine_interval, 
                        *self.unlock_args, 
                        "--callGasLimit", "0x493E0", 
                        "-f", self.provider+self.provider_suffix, 
                        f"-p {self.port}", 
                        "-v"]
        print("Starting ganache ...")
        try:
            process = subprocess.Popen(process_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            while 1:
                output = process.stdout.readline().decode("utf-8").strip()
                if output.startswith("Error"):
                    error = output
                    error_msg = error
                    while error:
                        error = process.stdout.readline().decode("utf-8")
                        error_msg += "\n" + error
                        if error.endswith("\n"):
                            break
                    raise Exception(error_msg)
                if output.startswith("Listening on "):
                    self.process = process
                    break
        except Exception as e:
            self.kill()
            raise e

    def increase_timestamp(self, increase):
        r = requests.post(self.node_path, json.dumps({"jsonrpc": "2.0","method": "evm_increaseTime", "params": [increase]}))
        return r.ok

    def mine(self):
        r = requests.post(self.node_path, json.dumps({"jsonrpc": "2.0","method": "evm_mine", "params": []}))
        return r.ok

    def stop_mining(self):
        r = requests.post(self.node_path, json.dumps({"jsonrpc": "2.0","method": "miner_stop", "params": []}))
        return r.ok        

    def start_mining(self):
        r = requests.post(self.node_path, json.dumps({"jsonrpc": "2.0","method": "miner_start", "params": [2]}))
        return r.ok

    def kill(self):
        if self.process:
            self.process.kill()