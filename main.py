"""
Wetterstation -> Hauptprogramm fuer Raspberry Pi Pico 2 + Grove Shield for Pi Pico.

TATSAECHLICHE PHYSISCHE VERKABELUNG (Stand: 22.08.2026):

  Sensor              Grove-Port   Pico-GPIO (SDA/SCL)              Bus-Typ
  ------------------  -----------  --------------------------       -------------------
  SHT30 (intern)      I2C0         GP8  / GP9                       Hardware I2C(0)
  QMP6988             I2C0         GP8  / GP9                       Hardware I2C(0)
  SHT30 (extern)      I2C1         GP6  / GP7                       Hardware I2C(1)
  MPU6886 (IMU)       A2           GP28 / <config.MPU6886_SCL_PIN>  SoftI2C
  AS7331 (UV)         D20          GP20 / <config.AS7331_SCL_PIN>   SoftI2C

Wichtig: QMP6988 sitzt auf demselben Breakout-Board wie der interne SHT30
("QMP6988" ist nur der Aufdruck auf dem Chip selbst) - beide haengen am
selben physischen Grove-I2C0-Stecker und damit am selben Bus. Es gibt daher
NUR 4 Busse, nicht 5.

Die beiden SoftI2C-Busse (MPU6886, AS7331) brauchen die zweite Signalader,
die noch per tools/i2c_pin_scan.py ermittelt und in config.py eingetragen
werden muss (config.MPU6886_SCL_PIN / config.AS7331_SCL_PIN). Solange diese
None sind, bricht dieses Skript beim Start kontrolliert mit einer klaren
Fehlermeldung ab, statt mit falscher Verkabelung stillschweigend zu misslingen.

Messintervall: siehe config.py (ACTIVE_PHASE = "test" -> alle 5s,
"pilot" -> alle 5min). Zum Umschalten NUR config.py aendern.
"""
import time
from machine import I2C, SoftI2C, Pin

import config
from drivers.sht30 import SHT30
from drivers.qmp6988 import QMP6988
from drivers.mpu6886 import MPU6886
from drivers.as7331 import AS7331
from drivers import solar_position

# Pin-Vollstaendigkeit pruefen, bevor irgendwas initialisiert wird
if config.MPU6886_SCL_PIN is None or config.AS7331_SCL_PIN is None:
    raise RuntimeError(
        "config.MPU6886_SCL_PIN und/oder config.AS7331_SCL_PIN sind noch nicht "
        "gesetzt (None). Bitte zuerst per tools/i2c_pin_scan.py ermitteln:\n"
        "  import i2c_pin_scan\n"
        "  i2c_pin_scan.find_sensor('A2', expected_address=0x68)\n"
        "  i2c_pin_scan.find_sensor('D20', expected_address=0x74)\n"
        "und die gefundenen SCL-Pins in config.py eintragen."
    )

# Vier getrennte I2C-Busse 
i2c_bus1_intern = I2C(0, scl=Pin(9), sda=Pin(8), freq=400_000)   # I2C0: SHT30-intern + QMP6988
i2c_bus2_extern = I2C(1, scl=Pin(7), sda=Pin(6), freq=100_000)   # I2C1: SHT30-extern
i2c_mpu6886 = SoftI2C(
    scl=Pin(config.MPU6886_SCL_PIN), sda=Pin(config.MPU6886_SDA_PIN), freq=100_000
)  # Port A2
i2c_as7331 = SoftI2C(
    scl=Pin(config.AS7331_SCL_PIN), sda=Pin(config.AS7331_SDA_PIN), freq=100_000
)  # Port D20


def scan_and_report(i2c, label):
    found = i2c.scan()
    print(f"[{label}] gefundene I2C-Adressen: {[hex(a) for a in found]}")
    return found


def safe_init(name, factory):
    """Initialisiert einen Sensor fehlertolerant, damit ein defekter/fehlender
    Sensor nicht das ganze Programm blockiert."""
    try:
        sensor = factory()
        print(f"[OK] {name} initialisiert")
        return sensor
    except Exception as e:
        print(f"[FEHLT] {name}: {e}")
        return None


def get_utc_now():
    """
    Liefert (year, month, day, hour, minute) in UTC.
    Der Pico 2 hat keine batteriegepufferte RTC - machine.RTC() startet nach
    jedem Reset bei 2021-01-01 00:00, falls sie nicht gesetzt wurde. Setzt sie
    entweder per NTP (nur mit Pico 2 W / WLAN, z.B. via ntptime.settime())
    oder manuell einmalig beim Boot, oder haengt ein externes RTC-Modul
    (z.B. DS3231) an einen freien Bus.
    """
    import machine
    rtc = machine.RTC()
    y, m, d, _wd, hh, mm, _ss, _sub = rtc.datetime()
    return y, m, d, hh, mm


def measure_all(sht30_int, sht30_ext, qmp6988, mpu6886, as7331):
    """Fuehrt eine komplette Messrunde durch und liefert dict mit allen Werten."""
    readings = {}

    if sht30_int:
        readings["sht30_intern"] = sht30_int.read()
    if sht30_ext:
        readings["sht30_extern"] = sht30_ext.read()
    if qmp6988:
        readings["qmp6988"] = qmp6988.read()
    if mpu6886:
        readings["mpu6886"] = mpu6886.read()
    if as7331:
        uv = as7331.read()
        year, month, day, hour, minute = get_utc_now()
        elevation = solar_position.solar_elevation_deg(
            year, month, day, hour, minute, config.STATION_LAT_DEG, config.STATION_LON_DEG
        )
        factor = solar_position.cosine_correction_factor(elevation, config.MIN_SUN_ELEVATION_DEG)

        uv["sun_elevation_deg"] = round(elevation, 1)
        
        if factor is not None:
            uv["uva_corrected"] = round(uv["uva_raw"] * factor, 1)
            uv["uvb_corrected"] = round(uv["uvb_raw"] * factor, 1)
            uv["uvc_corrected"] = round(uv["uvc_raw"] * factor, 1)
            # Optional: Korrigierter UV-Index ebenfalls auf Ganzzahl runden
            uv["uv_index_corrected"] = int(round(uv["uv_index"] * factor))
        else:
            uv["uva_corrected"] = None
            uv["uvb_corrected"] = None
            uv["uvc_corrected"] = None
            uv["uv_index_corrected"] = None

        readings["as7331"] = uv

    return readings


def main():
    print("== I2C Bus-Scan (4 Busse: I2C0 traegt 2 Sensoren) ==")
    scan_and_report(i2c_bus1_intern, "Bus 1 (I2C0): SHT30 intern + QMP6988")
    scan_and_report(i2c_bus2_extern, "Bus 2 (I2C1): SHT30 extern")
    scan_and_report(i2c_mpu6886, "Bus 3 (A2, SoftI2C): MPU6886")
    scan_and_report(i2c_as7331, "Bus 4 (D20, SoftI2C): AS7331")

    sht30_int = safe_init("SHT30 (intern)", lambda: SHT30(i2c_bus1_intern, address=0x44))
    qmp6988 = safe_init("QMP6988", lambda: QMP6988(i2c_bus1_intern, address=0x70))
    sht30_ext = safe_init("SHT30 (extern)", lambda: SHT30(i2c_bus2_extern, address=0x44))
    mpu6886 = safe_init("MPU6886", lambda: MPU6886(i2c_mpu6886, address=0x68))
    as7331 = safe_init("AS7331", lambda: AS7331(i2c_as7331, address=0x74))

    interval_s = config.get_interval_s()
    interval_ms = interval_s * 1000
    print(f"== Aktive Phase: '{config.ACTIVE_PHASE}' -> Messintervall {interval_s}s ==")

    last_measurement_ms = time.ticks_ms() - interval_ms  # sofort erste Messung ausloesen

    while True:
        now_ms = time.ticks_ms()
        if time.ticks_diff(now_ms, last_measurement_ms) >= interval_ms:
            last_measurement_ms = now_ms

            readings = measure_all(sht30_int, sht30_ext, qmp6988, mpu6886, as7331)

            print("---")
            for sensor_name, values in readings.items():
                print(f"{sensor_name}: {values}")

        time.sleep_ms(100)


if __name__ == "__main__":
    main()

