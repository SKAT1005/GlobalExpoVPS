import base64
import datetime
import json
import math
import time

import requests

first = datetime.datetime(year=2025, day=14, month=11, hour=22)

second = datetime.datetime.now()
print(math.ceil((second-first).total_seconds()/60/60))