"""
QMP6988 Luftdruck-/Temperatursensor fuer MicroPython.
Default I2C-Adresse: 0x70 (bei manchen Modulen 0x56 - ggf. per i2c.scan() pruefen)

Die Kompensation folgt dem im Datenblatt beschriebenen Polynom-Modell
(Koeffizienten a0,a1,a2 fuer Temperatur; b00,bt1,bt2,bp1,bp2,bp3,b11,b12,b21
fuer Druck). Rohdaten sind 24-bit, Nullpunkt der Kompensation liegt bei 2^23.

Funktioniert unveraendert mit machine.I2C (Hardware) UND machine.SoftI2C
(Software/Bit-Banging) - beide bieten dieselbe API (readfrom_mem/writeto_mem).
"""
import time
from machine import I2C

_REG_CHIP_ID = 0xD1
_REG_RESET = 0xE0
_REG_CTRL_MEAS = 0xF4      # Power-Mode + Oversampling
_REG_IO_SETUP = 0xF5
_REG_PRESS_MSB = 0xF7      # 3 Byte Druck, danach 3 Byte Temperatur
_REG_COE_START = 0xA0      # Kalibrierkoeffizienten, 25 Byte


class QMP6988:
    def __init__(self, i2c: I2C, address: int = 0x70):
        self.i2c = i2c
        self.address = address

        chip_id = self.i2c.readfrom_mem(self.address, _REG_CHIP_ID, 1)[0]
        if chip_id != 0x5C:
            raise RuntimeError(f"Unerwartete Chip-ID 0x{chip_id:02X} auf 0x{address:02X} - ist das wirklich der QMP6988?")

        self._read_calibration()
        # Normal-Mode, Oversampling x8 fuer Druck und Temperatur
        self.i2c.writeto_mem(self.address, _REG_CTRL_MEAS, bytes([0b01101101]))
        time.sleep_ms(20)

    def _read_calibration(self):
        raw = self.i2c.readfrom_mem(self.address, _REG_COE_START, 25)

        def s16(hi, lo):
            v = (hi << 8) | lo
            return v - 65536 if v > 32767 else v

        def s8(v):
            return v - 256 if v > 127 else v

        # Byte-Layout gemaess QMP6988-Datenblatt (Kap. Calibration Coefficients)
        self.COE_a0 = (s16(raw[0], raw[1]) << 4) | (raw[24] & 0x0F)
        self.COE_a1 = s16(raw[2], raw[3])
        self.COE_a2 = s16(raw[4], raw[5])
        self.COE_b00 = (s16(raw[6], raw[7]) << 4) | ((raw[24] >> 4) & 0x0F)
        self.COE_bt1 = s16(raw[8], raw[9])
        self.COE_bt2 = s16(raw[10], raw[11])
        self.COE_bp1 = s16(raw[12], raw[13])
        self.COE_b11 = s16(raw[14], raw[15])
        self.COE_bp2 = s16(raw[16], raw[17])
        self.COE_b12 = s16(raw[18], raw[19])
        self.COE_b21 = s16(raw[20], raw[21])
        self.COE_bp3 = s16(raw[22], raw[23])

    def read(self):
        """Liefert dict {'temperature_c': float, 'pressure_hpa': float}."""
        raw = self.i2c.readfrom_mem(self.address, _REG_PRESS_MSB, 6)

        dp_raw = (raw[0] << 16) | (raw[1] << 8) | raw[2]
        dt_raw = (raw[3] << 16) | (raw[4] << 8) | raw[5]

        dp = dp_raw - 2**23
        dt = dt_raw - 2**23

        # Temperaturkompensation (Ergebnis in 1/256 °C -> durch 256 teilen)
        tr = self.COE_a0 + self.COE_a1 * (dt / 2**23) + self.COE_a2 * (dt / 2**23) ** 2
        temperature_c = tr / 256.0

        # Druckkompensation (Ergebnis in Pa)
        pr = (self.COE_b00
              + self.COE_bt1 * (tr / 2**23)
              + self.COE_bp1 * (dp / 2**23)
              + self.COE_b11 * (dp / 2**23) * (tr / 2**23)
              + self.COE_bt2 * (tr / 2**23) ** 2
              + self.COE_bp2 * (dp / 2**23) ** 2
              + self.COE_b12 * (dp / 2**23) * (tr / 2**23) ** 2
              + self.COE_b21 * (dp / 2**23) ** 2 * (tr / 2**23)
              + self.COE_bp3 * (dp / 2**23) ** 3)
        pressure_hpa = pr / 100.0

        return {"temperature_c": round(temperature_c, 2), "pressure_hpa": round(pressure_hpa, 2)}
