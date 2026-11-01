# Kurze Erklaerung fuer den Aufbau der Sensoren ohne Ceilometer-Konstruktion
1. Python-Abhaengigkeiten installieren: Auf dem hostenden Raspberry Pi muessen die Pakete fuer die serielle Schnittstelle und den InfluxDB-Client installiert werden -> 1_Bash
2. Bridge-Skript anlegen (2_pico_to_influx.py): Erstelle auf dem Raspberry Pi ein Skript, welches die USB-Daten liest und an InfluxDB übermittelt -> 2_pico_to_influx.py
3. Als Systemd-Dienst einrichten (Autostart): Erstelle die Datei /etc/systemd/system/pico-bridge.service -> 3_Systemd-Dienst_einrichten_(Autostart)
4. Dienst aktivieren und starten -> 4_Bash-Dienst_aktivieren
