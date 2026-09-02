"""
Zentrale Konfiguration der Wetterstation.

Zum Umschalten zwischen Testphase und Pilot-/Freigabephase reicht es, unten
ACTIVE_PHASE zu aendern (z.B. per Thonny (o.Ä.) direkt auf dem Pico bearbeiten),
main.py selbst muss dafuer nicht angefasst werden.
"""

# Sekunden zwischen zwei vollstaendigen Messrunden, je nach Projektphase.
PHASES = {
    "test": 5,       # Testphase: engmaschig, zum Debuggen/Beobachten
    "pilot": 300,    # Pilot-/Freigabephase: 5 Minuten
}

# Hier die aktive Phase auswaehlen: "test" oder "pilot"
ACTIVE_PHASE = "test"


def get_interval_s():
    """Liefert das Messintervall in Sekunden fuer die aktuell aktive Phase."""
    if ACTIVE_PHASE not in PHASES:
        raise ValueError(f"Unbekannte Phase '{ACTIVE_PHASE}' - erlaubt: {list(PHASES.keys())}")
    return PHASES[ACTIVE_PHASE]


# Standort der Wetterstation (fuer die Sonnenstand-Korrektur des AS7331)
STATION_LAT_DEG = 47.69
STATION_LON_DEG = 8.75
MIN_SUN_ELEVATION_DEG = 5.0

"""
Tatsaechliche physische Verkabelung:

QMP6988 sitzt auf demselben Breakout-Board wie der interne SHT30 (gleicher
Grove-I2C0-Stecker, "QMP6988" ist nur der Aufdruck auf dem Chip) -> beide
teilen sich Bus 1 (I2C0), es sind KEINE eigene Verkabelung/kein eigener
Bus fuer den QMP6988 noetig.

MPU6886 (Port A2) und AS7331 (Port D20) haengen an je einem einzelnen
Grove-Anschluss. Die "Haupt-GPIO" jedes Ports ist dokumentiert, die zweite
Signalader (SDA oder SCL, je nachdem) ist auf dem Shield nicht zuverlaessig
dokumentiert. Bitte mit tools/i2c_pin_scan.py ermitteln (siehe README/Chat)
und hier eintragen, BEVOR main.py laeuft:
"""

MPU6886_SDA_PIN = 28   # A2-Hauptpin, dokumentiert
MPU6886_SCL_PIN = None  # TODO: per i2c_pin_scan.find_sensor("A2", 0x68) ermitteln

AS7331_SDA_PIN = 20    # D20-Hauptpin, dokumentiert
AS7331_SCL_PIN = None  # TODO: per i2c_pin_scan.find_sensor("D20", 0x74) ermitteln
