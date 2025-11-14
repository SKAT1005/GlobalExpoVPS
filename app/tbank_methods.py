import datetime
import hashlib
import uuid

import requests


url = 'https://securepay.tinkoff.ru'
termKey = '1760506943724DEMO'
passw = '2_pfWcw$%SoJI*Z_'


def generate_order_id(prefix="ORD"):
    now = datetime.datetime.now()
    date_part = now.strftime("%Y%m%d-%H%M%S")
    random_part = uuid.uuid4().hex[:8].upper()
    order_id = f"{prefix}-{date_part}-{random_part}"
    return order_id


def generateToken(data: dict):
    data['Password'] = passw
    flat_data = {k: v for k, v in data.items() if not isinstance(v, (dict, list))}
    sorted_items = sorted(flat_data.items(), key=lambda x: x[0])
    concatenated = "".join(str(value) for _, value in sorted_items)
    token = hashlib.sha256(concatenated.encode("utf-8")).hexdigest()
    return token


def create_tbank_payment(amount: str):
    data = {"TerminalKey": termKey,
            "Amount": int(amount + "00"),
            "OrderId": generate_order_id(),
            "Description": 'Test payment'}
    data['Token'] = generateToken(data)
    print(data)
    req = requests.post(url + '/v2/Init', json=data)
    print(req.json())
    return req.json()


def get_payment_status(paymentId: str):
    data = {"TerminalKey": termKey,
            "PaymentId": paymentId}
    data['Token'] = generateToken(data)
    req = requests.post(url + '/v2/GetState', json=data)
    return req.json().get('Status')
