from collections import defaultdict 
import csv
from pprint import pprint


class Graph:
	
	def __init__(self, instructions, hop_limit):
		self.graph = self._make_graph(instructions)
		self.origin = "ETH"
		self.destination = "ETH"
		self.exceptiontkn_symbol = "WETH"
		self.exceptiontkn_abi = "./abis/weth.json"
		self.max_hops = hop_limit

		self._paths = []

	def _make_graph(self, instructions):
		graph = defaultdict(list)
		for instruction in instructions:
			if instruction["enabled"] == "FALSE": continue
			instruction["siblings"] = find_sibling_instructions(instructions, instruction)
			graph[instruction["from_symbol"]].append(instruction)

		return graph

	def _find_paths(self, current_symbol, path, hops):

		# Save the path that arrives at the destination
		if current_symbol.upper()==self.destination and hops!=0:
			self._paths.append(path)
		else:
			# Increase the max number of hops for each weth symbol in the path
			exceptiontkn_at_start = current_symbol==self.exceptiontkn_symbol and len(path)==1
			exceptiontkn_at_end = current_symbol==self.exceptiontkn_symbol and hops==self.max_hops
			if exceptiontkn_at_start or exceptiontkn_at_end:
				hops -= 1
			# Finish only when max_hops are reached
			if hops != self.max_hops:
				for i in self.graph[current_symbol]:
					# Check that instruction and its sibling weren't used already
					inst_used = i in path
					sib_instr_used = any(sib for sib in i["siblings"] if sib in path)


					if (not (inst_used or sib_instr_used)) or i["execute_abi"]==self.exceptiontkn_abi:
						self._find_paths(i["to_symbol"], path+[i], hops+1)

	def find_all_paths(self):
		self._find_paths(self.origin, [], 0)

		return self._paths


def print_paths(paths):
	formatted_paths = []
	for path in paths:
		formatted_paths.append(" -> ".join([f"{i['from_symbol']}|{i['no']}|{i['to_symbol']}" for i in path]))

	pprint(formatted_paths, width=100)


def filter_by_symbol(paths, symbol):
	return [path for path in paths if any([i["to_symbol"]==symbol for i in path])]


def filter_by_length(paths, length):
	return [path for path in paths if len(path)==length]


def find_sibling_instructions(instructions, instruction):
	cond1 = lambda i: i["from_symbol"]==instruction["to_symbol"]
	cond2 = lambda i: i["to_symbol"]==instruction["from_symbol"]
	cond3 = lambda i: i["contract_address"]==instruction["contract_address"]
	siblings = [i for i in instructions if (cond1(i) and cond2(i) and cond3(i))]

	return siblings


def print_stats(paths):
	paths_counts = {}
	i = 2
	while 1:
		paths_count = len(filter_by_length(paths, i))
		if paths_count:
			paths_counts[i] = paths_count
			i += 1
		else:
			break

	print("Instruction count set to: ", g1.max_hops)
	print("Paths by instruction count: ", paths_counts)
	print("All paths: ", sum(paths_counts.values()))


if __name__ == "__main__":
	with open('instructions4.csv', newline='') as csvfile:
		instructions = list(csv.DictReader(csvfile))

	g1 = Graph(instructions, hop_limit=2)
	paths = g1.find_all_paths()

	# paths = filter_by_symbol(paths, "USDC")
	paths = filter_by_length(paths, 4)
	print(len(paths))

	print_paths(paths)

	 #print_stats(paths)
