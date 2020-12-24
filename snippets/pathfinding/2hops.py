import csv
from pprint import pprint
import itertools as it


def format_instuction(instruction):
	return f"{instruction['from_symbol']}|{instruction['to_symbol']}"


def path_finder0(start_assets, end_assets, ghost_tokens):

	def path_finder(parent_instruction, hops):
		if hops == allowed_hops or parent_instruction["to_symbol"] in ghost_tokens:
			children = [instruction for instruction in instructions if instruction["enabled"].lower()=="true" and instruction["from_symbol"]==parent_instruction["to_symbol"] and instruction["to_symbol"] in ghost_tokens and instruction["contract_address"] != parent_instruction["contract_address"]]
			if not children:
				children = [format_instuction(instruction) for instruction in instructions if instruction["enabled"].lower()=="true" and instruction["from_symbol"]==parent_instruction["to_symbol"] and instruction["to_symbol"] in end_assets and instruction["contract_address"] != parent_instruction["contract_address"]]
				return children if children else None
		else:
			children = [instruction for instruction in instructions if instruction["enabled"].lower() == "true" and instruction["from_symbol"]==parent_instruction["to_symbol"] and instruction["contract_address"] != parent_instruction["contract_address"]]
		# pprint(instruction)
		# pprint(children[0])
		
		paths = []
		for child in children:
			if child["to_symbol"] in base_tokens:
				# paths.append([child]) 
				continue
			find = path_finder(child, hops+1)
			# pprint(find)
			# exit()
			if find:
				# print(f"{parent_instruction['from_symbol']} - {parent_instruction['to_symbol']}")
				paths.append([format_instuction(child), find])

		return paths


	start_instructions = [instruction for instruction in instructions if instruction["enabled"].lower() == "true" and instruction["from_symbol"] in start_assets]
	hops = 2
	paths = []
	for instruction in start_instructions:
		if instruction["to_symbol"] in end_assets: continue 
		ghost = instruction["to_symbol"] in ghost_tokens
		find = path_finder(instruction, hops - ghost)
		if find:
			paths.append([format_instuction(instruction), find])

	return paths





def extend_paths(paths):

	extended = []

	def unnest(selections, assets):
		for selection in selections:
			# pprint(selection); exit()

			asset = selection[0]
			paths = selection[1]
			# print("asset", asset)
			# print("paths", paths)
			# print("asset", asset)
			if (len(paths) > 1 and type(paths[1]) == list) or (len(paths)==1 and type(paths[0]) == list):
				unnest(paths, assets + [asset])
			else:
				# print(paths)
				for path in paths:
					extended.append(assets + [asset, path])
					pprint(assets + [asset, path])
			
			

	unnest(paths, [])

	return extended
	

def list_opportunities(*args):
	paths = path_finder0(*args)
	# pprint(paths[0])
	extend_paths_lst = extend_paths(paths)

	return extend_paths_lst


if __name__ == "__main__":
	with open('instructions2.csv', newline='') as csvfile:
		instructions = list(csv.DictReader(csvfile))

	allowed_hops = 2
	base_tokens = ["ETH"]
	ghost_tokens = ["WETH"]

	opportunities = list_opportunities(base_tokens, base_tokens, ghost_tokens)

	# for pair in it.product(base_tokens, repeat=2):
	# 	opp_instance = list_opportunities(pair[0], pair[1])
	# 	opportunities += opp_instance
	# 	print(f"{pair}: {len(opp_instance)}")

	# print("_"*50, f"\nTotal: {len(opportunities)}")
	# pprint([[f"{step['from_symbol']}-{step['to_symbol']}" for step in opportunity] for opportunity in opportunities])
	# print([opportunity for opportunity in opportunities if opportunity[0]["contract_address"]==opportunity[1]["contract_address"]])
	# print("\nNote, this is only for 3 hops.")
	# paths = path_finder0()
	# pprint(paths[0])
	





