import requests
from pprint import pprint


url = "http://localhost:3000/fetch_reserves"
r = requests.get(url)
r_json = r.json()
formatted = {p['id']: {k: int(v, 16) for k, v in p['reserve'].items()} for p in r_json}
pprint(formatted)