"""
SHT30 Treiber (Sensirion) fuer MicroPython auf dem Raspberry Pi Pico 2.
Wird sowohl fuer den internen als auch den externen SHT30 verwendet,
einfach mit unterschiedlichem I2C-Bus instanziieren.

Default I2C-Adresse: 0x44 (ADDR-Pin auf GND)
Alternative Adresse: 0x45 (ADDR-Pin auf VDD)

Funktioniert unveraendert mit machine.I2C (Hardware) UND machine.SoftI2C
(Software/Bit-Banging), beide bieten dieselbe API (writeto/readfrom).
"""
import time
from machine import I2C

_CMD_MEASURE_HIGH_REP = b'\x24\x00'  # single shot, high repeatability, kein clock stretching
_CMD_SOFT_RESET = b'\x30\xA2'


class SHT30:
    def __init__(self, i2c: I2C, address: int = 0x44):
        self.i2c = i2c
        self.address = address
        self.reset()

    def reset(self):
        try:
            self.i2c.writeto(self.address, _CMD_SOFT_RESET)
            time.sleep_ms(5)
        except OSError as e:
            raise RuntimeError(f"SHT30 (0x{self.address:02X}) nicht erreichbar: {e}")

    @staticmethod
    def _crc8(data: bytes) -> int:
        crc = 0xFF
        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ 0x31) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    def read(self):
        """Liefert dict {'temperature_c': float, 'humidity_rh': float} oder None bei CRC-Fehler."""
        self.i2c.writeto(self.address, _CMD_MEASURE_HIGH_REP)
        time.sleep_ms(15)  # High-Repeatability-Messzeit lt. Datenblatt max. 15 ms
        raw = self.i2c.readfrom(self.address, 6)

        t_raw, t_crc = raw[0:2], raw[2]
        h_raw, h_crc = raw[3:5], raw[5]

        if self._crc8(t_raw) != t_crc or self._crc8(h_raw) != h_crc:
            return None

        t_ticks = (t_raw[0] << 8) | t_raw[1]
        h_ticks = (h_raw[0] << 8) | h_raw[1]

        temperature_c = -45 + 175 * (t_ticks / 65535)
        humidity_rh = 100 * (h_ticks / 65535)

        return {"temperature_c": round(temperature_c, 2), "humidity_rh": round(humidity_rh, 2)}
