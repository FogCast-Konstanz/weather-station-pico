# Raspberry Pi Pico 2 Wetterstation

Dieses Repository enthält den MicroPython-Code für eine autarke, modulare Wetterstation auf Basis des Raspberry Pi Pico 2. Das System erfasst Umweltparameter (Temperatur, Luftfeuchtigkeit, Luftdruck) sowie Bewegungsdaten (IMU) und berechnet einen dynamisch korrigierten UV-Index.

## 📂 Projektstruktur

* `main.py`: Die Hauptausführungsschleife (nicht-blockierend)[cite: 10].
* `config.py`: Zentrale Konfigurationsdatei für Intervalle, Standortdaten und Pin-Mappings.
* `drivers/`: Hardware-spezifische MicroPython-Treiber für AS7331, MPU6886, QMP6988, SHT30 sowie die Sonnenstandsberechnung[cite: 12, 13, 14, 15, 16].
* `tools/`: Hilfsskripte, insbesondere `i2c_pin_scan.py` zur Ermittlung verdeckter I²C-Pins am Grove Shield[cite: 9].
* `docs/`: Projektdokumentation, Hardware-Aufbau und Gehäuseskizzen.

## 🚀 Installation & Setup

1. **MicroPython flashen:** Stelle sicher, dass auf dem Pico 2 die aktuelle MicroPython-Firmware installiert ist.
2. **Dateien übertragen:** Öffne Thonny und kopiere alle Dateien und Ordner (außer `.git` und `docs/`) auf das Hauptverzeichnis (`/`) des Pico 2.
3. **SoftI²C-Pins ermitteln:** Da die zweite Signalader bei den Grove-Ports `A2` (IMU) und `D20` (UV) je nach Shield variieren kann, führe einmalig das Diagnose-Skript aus:
   ```python
   import tools.i2c_pin_scan
   tools.i2c_pin_scan.find_sensor("A2", expected_address=0x68)
   tools.i2c_pin_scan.find_sensor("D20", expected_address=0x74)
