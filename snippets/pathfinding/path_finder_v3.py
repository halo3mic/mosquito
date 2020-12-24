import csv
from pprint import pprint
import itertools as it



def format_instuction(instruction):
	return f"{instruction['from_symbol']}|{instruction['to_symbol']}"


def path_finder0(start_assets, end_assets, allowed_hops, instructions):

	def path_finder(parent_instruction, hops):
		filter1 = lambda child, parent: child["enabled"].lower()=="true" and child["from_symbol"]==parent["to_symbol"] and not (child["contract_address"] == parent["contract_address"] and child["to_symbol"]==parent["to_symbol"])
		filter2 = lambda child: child["to_symbol"] in end_assets
		if hops == allowed_hops:
			children = [format_instuction(instruction) for instruction in instructions if filter1(instruction, parent_instruction) and filter2(instruction)]
			return children if children else None
		
		children = [instruction for instruction in instructions if filter1(instruction, parent_instruction)]
		
		paths = []
		for child in children:
			if child["to_symbol"] in end_assets:
				# paths.append([child]) 
				continue
			find = path_finder(child, hops+1)
			if find:
				paths.append([format_instuction(child), find])

		return paths


	start_instructions = [instruction for instruction in instructions if instruction["enabled"].lower() == "true" and instruction["from_symbol"] in start_assets]
	hops = 2
	paths = []
	for instruction in start_instructions:
		if instruction["to_symbol"] in end_assets: continue 
		find = path_finder(instruction, hops)
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
			
			

	unnest(paths, [])

	return extended
	

def list_opportunities(base_tokens, allowed_hops, instructions):
	paths = path_finder0(base_tokens, base_tokens, allowed_hops, instructions)
	# pprint(paths[0])
	extend_paths_lst = extend_paths(paths)

	return extend_paths_lst


def weth_exception(opportunities):
	opportunities_final = []
	for opp in opportunities:
		a = opp[0].startswith("WETH")
		b = opp[-1].endswith("WETH")
		if not (a or b):
			opportunities_final.append(opp)
			continue

		new_opp = opp.copy()
		if a: new_opp.insert(0, "ETH|WETH")
		if b: new_opp.append("WETH|ETH")
		opportunities_final.append(new_opp)

	return opportunities_final

def print_opps(opportunities):
	for opp in opportunities:
		opp_formatted = " -> ".join(opp)
		print(opp_formatted)


if __name__ == "__main__":
	with open('instructions4.csv', newline='') as csvfile:
		instructions = list(csv.DictReader(csvfile))
	
	opportunities_client_2h = list_opportunities(["ETH"], 2, instructions)
	opportunities_client_3h = list_opportunities(["ETH"], 3, instructions)

	opportunities_new_2h = weth_exception(list_opportunities(["ETH", "WETH"], 2, instructions))
	opportunities_new_3h = weth_exception(list_opportunities(["ETH", "WETH"], 3, instructions))

	# print_opps(opportunities_net_3h)
	# print(len(opportunities_net_3h))
	opp_count = {"opportunities_client_2h": len(opportunities_client_2h), 
				 "opportunities_client_3h": len(opportunities_client_3h), 
				 "opportunities_new_2h": len(opportunities_new_2h),
				 "opportunities_new_3h": len(opportunities_new_3h)
				 }
	# print(opp_count)
	pprint(instructions)






