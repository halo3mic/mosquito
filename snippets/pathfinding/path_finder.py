import csv
from pprint import pprint
import itertools as it


def path_finder(current_asset, hops):
	if hops == allowed_hops - 1:
		children = [[instruction["from_symbol"], [instruction["to_symbol"]]] for instruction in instructions if instruction["enabled"].lower() == "true" and instruction["from_symbol"] == current_asset and instruction["to_symbol"] == end_asset]

		return children if children else None

	children = [instruction for instruction in instructions if instruction["enabled"].lower() == "true" and instruction["from_symbol"] == current_asset]

	paths = []
	for child in children:
		if child["to_symbol"] == end_asset:
			# paths.append([current_asset] + [[end_asset]])
			continue  # PREVENT ONLY TWO HOPS!!!
		find = path_finder(child["to_symbol"], hops+1)
		if find:
			paths.append([current_asset]+find)

	return paths


def extend_paths(paths):

	extended = []

	def unnest(selections, assets):
		if not selections:
			extended.append(assets + selections)

		for selection in selections:
			asset = selection[0]
			paths = selection[1:]
			unnest(paths, assets + [asset])

	unnest(paths, [])

	return extended
	

def list_opportunities(start_asset, end_asset_):
	global end_asset
	end_asset = end_asset_
	paths = path_finder(start_asset, 0)
	extend_paths_lst = extend_paths(paths)

	return extend_paths_lst


if __name__ == "__main__":
	with open('instructions2.csv', newline='') as csvfile:
		instructions = list(csv.DictReader(csvfile))

	allowed_hops = 2
	base_tokens = ["ETH", "WETH"]

	opportunities = []
	for pair in it.product(base_tokens, repeat=2):
		opp_instance = list_opportunities(pair[0], pair[1])
		opportunities += opp_instance
		print(f"{pair}: {len(opp_instance)}")

	print("_"*50, f"\nTotal: {len(opportunities)}")
	pprint([opportunity for opportunity in opportunities if "WETH" in opportunity])
	print("\nNote, this is only for 3 hops.")
	





