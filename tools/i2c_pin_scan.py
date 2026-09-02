"""
Diagnose-Hilfsskript: findet heraus, welche zwei Pico-GPIOs hinter einem
bestimmten Grove-Anschluss (z.B. A2 oder D20) als SDA/SCL liegen.

WARUM DIESES SKRIPT NOETIG IST:
Fuer I2C0/I2C1 sind SDA/SCL eindeutig dokumentiert (GP8/GP9 bzw. GP6/GP7).
Fuer die "zweckentfremdeten" Analog-/Digital-Ports (A0-A2, D16/D18/D20) ist
in der oeffentlichen Seeed-Doku nur die jeweils EINE "Haupt-GPIO" (z.B. D20
-> GP20) sicher belegt, welche GPIO auf der zweiten Signalader des
Grove-Steckers liegt, ist nicht zuverlaessig dokumentiert und kann je nach
Shield-Revision leicht variieren. Am zuverlaessigsten ist der Aufdruck direkt
auf eurem Shield (Silkscreen neben dem jeweiligen Grove-Stecker) - falls
lesbar, dort zuerst nachsehen. Dieses Skript ist der Plan B: einfach alle
sinnvollen GPIO-Nachbarn ausprobieren und schauen, wo der Sensor antwortet.

VERWENDUNG (direkt ueber die Thonny-REPL (o.Ä.) auf dem Pico ausfuehren):
    >>> import i2c_pin_scan
    >>> i2c_pin_scan.find_sensor("D20", expected_address=0x74)
"""
from machine import SoftI2C, Pin
import time

# Bekannte "Haupt-GPIO" je Port (sicher dokumentiert) + Kandidaten fuer die
# zweite Signalader (Nachbar-Pins, typische Shield-Layouts).
PORT_CANDIDATES = {
    "A0": (26, [27, 22, 3]),
    "A1": (27, [26, 28, 22]),
    "A2": (28, [27, 22, 3]),
    "D16": (16, [17, 22, 3]),
    "D18": (18, [19, 22, 3]),
    "D20": (20, [21, 22, 3]),
}


def find_sensor(port_name, expected_address=None, freq=100_000):
    """
    Probiert die Haupt-GPIO des Ports als SDA UND als SCL durch, jeweils
    gepaart mit mehreren Kandidaten fuer die zweite Ader. Gibt die
    funktionierende Pin-Kombination zurueck (oder None).
    """
    if port_name not in PORT_CANDIDATES:
        raise ValueError(f"Unbekannter Port '{port_name}', erlaubt: {list(PORT_CANDIDATES.keys())}")

    main_pin, candidates = PORT_CANDIDATES[port_name]

    for other_pin in candidates:
        for sda, scl in [(main_pin, other_pin), (other_pin, main_pin)]:
            try:
                i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda), freq=freq)
                time.sleep_ms(20)
                found = i2c.scan()
                print(f"[Test] sda=GP{sda} scl=GP{scl} -> gefunden: {[hex(a) for a in found]}")
                if found and (expected_address is None or expected_address in found):
                    print(f"==> TREFFER fuer {port_name}: sda=GP{sda}, scl=GP{scl}")
                    return sda, scl
            except Exception as e:
                print(f"[Fehler] sda=GP{sda} scl=GP{scl}: {e}")

    print(f"Kein funktionierendes Pin-Paar fuer {port_name} gefunden. "
          f"Bitte Silkscreen auf dem Shield pruefen oder Kandidatenliste erweitern.")
    return None
