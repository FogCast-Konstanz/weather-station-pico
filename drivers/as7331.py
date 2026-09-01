"""
AS7331 Spectral UVA/B/C Sensor (ams OSRAM) fuer MicroPython.
Default I2C-Adresse: 0x74 (per A0/A1-Pins auf 0x74-0x77 einstellbar)

WICHTIGER HINWEIS:
Der AS7331 hat zwei Register-Zustaende (Configuration-State / Measurement-State),
zwischen denen ueber das OSR-Register (Bit SS) umgeschaltet wird. Das Adressschema
unten basiert auf der oeffentlichen Datenblatt-Struktur, wurde hier aber NICHT an
echter Hardware verifiziert. Bevor produktiv genutzt: unbedingt Kapitel "Register
Map" im Datenblatt (DS001047) neben die Register-Konstanten legen und mit einem
Logic Analyzer / i2c.scan() gegenpruefen. Alternativ: die bestehende Arduino-
Bibliothek von RobTillaart oder SparkFun als Referenz portieren, statt diesem
Treiber blind zu vertrauen.

Funktioniert unveraendert mit machine.I2C (Hardware) UND machine.SoftI2C
(Software/Bit-Banging) - beide bieten dieselbe API (readfrom_mem/writeto_mem).
"""
import time
from machine import I2C

_REG_OSR = 0x00     # Operational State Register (in beiden States vorhanden)
_REG_CREG1 = 0x02   # Configuration State: Gain / Time
_REG_MRES1 = 0x02   # Measurement State: UVA (2 Byte)
_REG_MRES2 = 0x03   # Measurement State: UVB (2 Byte)
_REG_MRES3 = 0x04   # Measurement State: UVC (2 Byte)
_REG_TEMP = 0x01    # Measurement State: Chip-Temperatur (2 Byte)

_OSR_SS_START_MEASURE = 0x83  # Power-on + Start + Measurement-Mode (CMD-Mode)
_OSR_SS_CONFIG = 0x02         # zurueck in Configuration-State


class AS7331:
    def __init__(self, i2c: I2C, address: int = 0x74, gain: int = 0x09, time_reg: int = 0x09):
        """
        gain / time_reg sind Rohwerte fuer CREG1 (obere/untere Nibble) -
        Default entspricht einer moderaten Empfindlichkeit/Integrationszeit.
        Siehe Datenblatt Tabelle CREG1 fuer die genaue Zuordnung.
        """
        self.i2c = i2c
        self.address = address

        # In Konfigurationszustand wechseln und Gain/Time setzen
        self.i2c.writeto_mem(self.address, _REG_OSR, bytes([_OSR_SS_CONFIG]))
        creg1 = ((gain & 0x0F) << 4) | (time_reg & 0x0F)
        self.i2c.writeto_mem(self.address, _REG_CREG1, bytes([creg1]))
        time.sleep_ms(5)

    def read(self):
        """Startet eine Einzelmessung und liefert dict uva/uvb/uvc + uv_index (Ganzzahl)."""
        self.i2c.writeto_mem(self.address, _REG_OSR, bytes([_OSR_SS_START_MEASURE]))

        # Wartezeit muss zur eingestellten Integrationszeit (CREG1:TIME) passen
        time.sleep_ms(50)

        temp_raw = self.i2c.readfrom_mem(self.address, _REG_TEMP, 2)
        uva_raw = self.i2c.readfrom_mem(self.address, _REG_MRES1, 2)
        uvb_raw = self.i2c.readfrom_mem(self.address, _REG_MRES2, 2)
        uvc_raw = self.i2c.readfrom_mem(self.address, _REG_MRES3, 2)

        def le16(b):
            return b[0] | (b[1] << 8)

        uva = le16(uva_raw)
        uvb = le16(uvb_raw)
        uvc = le16(uvc_raw)

        # 1. UV-Index Formel berechnen
        uvi_calibration = 0.077  # Dein ermittelter Faktor ohne Schutzglas
        uvi_estimator = (uvb * 1.0) + (uva * 0.001)
        raw_uv_index = uvi_estimator * uvi_calibration

        # 2. Auf Ganzzahl runden (z. B. 3.4 -> 3, 3.6 -> 4)
        uv_index_rounded = int(round(raw_uv_index))

        # Temperatur-Umrechnung laut Datenblatt
        temperature_c = le16(temp_raw) * 0.05

        return {
            "uva_raw": uva,
            "uvb_raw": uvb,
            "uvc_raw": uvc,
            "uv_index": uv_index_rounded,  # Neuer gerundeter Ganzzahl-Wert
            "temperature_c": round(temperature_c, 2),
        }

