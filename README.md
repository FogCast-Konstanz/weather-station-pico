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
2. **Dateien übertragen:** Öffne Thonny (oder ähnliches) und kopiere alle Dateien und Ordner (außer `.git` und `docs/`) auf das Hauptverzeichnis (`/`) des Pico 2.
3. **SoftI²C-Pins ermitteln:** Da die zweite Signalader bei den Grove-Ports `A2` (IMU) und `D20` (UV) je nach Shield variieren kann, führe einmalig das Diagnose-Skript aus:
   ```python
   import tools.i2c_pin_scan
   tools.i2c_pin_scan.find_sensor("A2", expected_address=0x68)
   tools.i2c_pin_scan.find_sensor("D20", expected_address=0x74)
4. **Messwerte überprüfen:** Wenn die Skripte auf den Pico hochgeladen sind, können die ersten Messwerte auf der Konsole von dem PC ausgegeben werden. Hierbei können die Messwerte auf realitätsnahe Werte überprüft werden.

## ⏭️ Aktueller Stand / Weitere Schritte für das kommende Team

Momentan befindet sich der Aufbau der Sensorenanlage in den finalen Schritten. 

### Montage

Die Montage der 3D-Druck Teile und den Sensoren wir in diesem Repository unter folgenden Link erläutert:
https://github.com/FogCast-Konstanz/weather-station-pico/tree/main/docs/3D-Druck_Aufbau

### Die Stromversorgung

- Verwendete Komponenten:
   - Mikrocontroller: **Raspberry Pi Pico 2** 
   - Schaltmodul: **Seeed Studio Grove 2-Kanal-Relaismodul** (im transparenten Schutzgehäuse).
      - Verwendet zwei Songle SRD-05VDC-SL-C Relais (5V-Spulenspannung).
      - Schalteleistung: max. 10 A bei 250 V AC (Wechselstrom) bzw. 10 A bei 30 V DC (Gleichstrom).

- Verbindung & Funktion:
   - Verkabelung: Das Relaismodul ist über ein 4-adriges Kabel (Signal, 5V, GND) mit einem Steckplatz des Pico-Shields verbunden.
   - Funktionsweise: Das Relais fungiert als elektronisch gesteuerter Schalter. Der Raspberry Pi Pico 2 kann über einen digitalen Ausgang ein Steuersignal an das Modul senden, um den Stromkreis auf der Lastseite (Schraubklemmen am Relais) zu schließen oder zu öffnen.
   - Sicherheit: Das Modul verfügt über eine integrierte Optokoppler-Isolierung, die den empfindlichen Mikrocontroller vor gefährlichen Spannungsspitzen und Rückströmen aus dem Laststromkreis schützt.

### Die Sensoren sind mit dem Raspberry Pi Pico 2 wie folgt verbunden:

 Sensor              Grove-Port   Pico-GPIO (SDA/SCL)              Bus-Typ
  ------------------  -----------  --------------------------       -------------------
  SHT30 (intern)      I2C0         GP8  / GP9                       Hardware I2C(0)
  QMP6988             I2C0         GP8  / GP9                       Hardware I2C(0)
  SHT30 (extern)      I2C1         GP6  / GP7                       Hardware I2C(1)
  MPU6886 (IMU)       A2           GP28 / <config.MPU6886_SCL_PIN>  SoftI2C
  AS7331 (UV)         D20          GP20 / <config.AS7331_SCL_PIN>   SoftI2C

Diese Verkabelung ist in 'main.py' im Code wiederzufinden, dementsprechend kann man dies im Code und physisch verändern, wenn man das möchte.

