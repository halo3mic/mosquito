import requests


def fetch_gas_price():
    url = "https://gasnow.sparkpool.com/api/v3/gas/price"
    r = requests.get(url).json()
    if r["code"] != 200:
        return None
    return r["data"]


if __name__ == "__main__":
    gas_price = fetch_gas_price()
    print(gas_price)
