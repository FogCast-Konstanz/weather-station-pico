import serial
import json
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# InfluxDB Konfiguration - MUSS NOCH ANGEPASST WERDEN
INFLUX_URL = "http://localhost:8086"
INFLUX_TOKEN = "DEIN_INFLUX_TOKEN"
INFLUX_ORG = "deine_org"
INFLUX_BUCKET = "wetterstation"

# Serielle Schnittstelle (Pico 2)
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 115200

client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

ser = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)

print(f"Verbindung zu Pico 2 an {SERIAL_PORT} hergestellt. Warte auf Messdaten...")

while True:
    try:
        line = ser.readline().decode('utf-8').strip()
        if line and line.startswith("{") and line.endswith("}"):
            data = json.loads(line)
            
            # InfluxDB Point erstellen
            point = Point("weather_measurement")
            
            if "as7331" in data:
                point.field("uv_index", data["as7331"].get("uv_index", 0))
                point.field("uva_raw", data["as7331"].get("uva_raw", 0))
                point.field("uvb_raw", data["as7331"].get("uvb_raw", 0))
                
            if "sht30_extern" in data:
                point.field("temp_ext", data["sht30_extern"].get("temperature_c", 0.0))
                point.field("humidity_ext", data["sht30_extern"].get("humidity_rh", 0.0))
                
            if "qmp6988" in data:
                point.field("pressure_hpa", data["qmp6988"].get("pressure_hpa", 0.0))
                
            write_api.write(bucket=INFLUX_BUCKET, org=INFLUX_ORG, record=point)
            print(f"[OK] Daten erfolgreich in InfluxDB geschrieben: {data}")
            
    except Exception as e:
        print(f"[Fehler] {e}")
        time.sleep(2)
