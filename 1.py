import time

import requests

api_key = '0658bb976cf550df03209d4b465b0a85c25eaa0010564495f7fa75b18b938036'
CHAT_ID = -5063638309
headers = {
    'X-API-KEY': api_key
}
buy_server_url = 'https://api.serverspace.ru/api/v1/servers'
data = {'location_id': 'ds1', 'image_id': 'Ubuntu-24.04.2-X64', 'cpu': 2, 'ram_mb': 4096,
        'volumes': [{'name': 'boot', 'size_mb': 51200}], 'networks': [{'bandwidth_mbps': 50}],
        'name': 'c2xhdmF0dWtpbkBtYWlsLnJ1XzE3NjMyNzMyNjA', 'server_init_script': 'sudo apt update'}
responce = requests.post(url=buy_server_url, json=data, headers=headers).json()
task_id = responce['task_id']
print(task_id)
get_task_url = f'https://api.serverspace.ru/api/v1/tasks/{task_id}'
while True:
    responce = requests.get(url=get_task_url, headers=headers).json()
    print(responce)
    time.sleep(5)
