import random
import time
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision

url = "http://localhost:8086"
token = "YfRVMDNRL349HKwJPNSh-0PmzBjTqIqWgCskDLXaJWXhyIv8KPbUEzuPtBtb9wBXkZbpGJst7RFbkO7EDEsIvg=="
org = "cnc-org"
bucket = "cnc_data"

client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api()

while True:
    vibration = round(random.uniform(6.0, 9.0), 2)
    temperature = round(random.uniform(30, 90), 2)
    rpm = random.randint(1000, 5000)

    point = (
        Point("cnc_machine")
        .field("vibration", vibration)
        .field("temperature", temperature)
        .field("rpm", rpm)
        .time(datetime.now(), WritePrecision.NS)   # changed line
    )

    write_api.write(bucket=bucket, org=org, record=point)

    print("Data sent:", vibration, temperature, rpm)
    time.sleep(2)