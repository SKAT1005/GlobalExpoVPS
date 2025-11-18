import time

import requests

api_key = '0658bb976cf550df03209d4b465b0a85c25eaa0010564495f7fa75b18b938036'
CHAT_ID = -5063638309
headers = {
    'X-API-KEY': api_key
}
buy_server_url = 'https://api.serverspace.ru/api/v1/locations'
data = {'location_id': 'ds1', 'image_id': 'Ubuntu-24.04.2-X64', 'cpu': 2, 'ram_mb': 4096,
        'volumes': [{'name': 'boot', 'size_mb': 51200}], 'networks': [{'bandwidth_mbps': 50}],
        'name': 'c2xhdmF0dWtpbkBtYWlsLnJ1XzE3NjMyNzMyNjA', 'server_init_script': 'sudo apt update'}
responce = requests.get(url=buy_server_url, json=data, headers=headers).json()
print(responce)
