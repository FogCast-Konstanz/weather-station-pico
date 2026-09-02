"""
MPU6886 6-Achsen IMU (Accel + Gyro) fuer MicroPython.
Default I2C-Adresse: 0x68 (AD0=GND) bzw. 0x69 (AD0=VDD)

Funktioniert unveraendert mit machine.I2C (Hardware) UND machine.SoftI2C
(Software/Bit-Banging), beide bieten dieselbe API (readfrom_mem/writeto_mem).
"""
import time
from machine import I2C

_REG_WHO_AM_I = 0x75
_REG_PWR_MGMT_1 = 0x6B
_REG_ACCEL_CONFIG = 0x1C
_REG_GYRO_CONFIG = 0x1B
_REG_ACCEL_XOUT_H = 0x3B  # danach: Accel(6) + Temp(2) + Gyro(6) am Stueck lesbar

_ACCEL_SCALE_2G = 16384.0   # LSB pro g bei +-2g
_GYRO_SCALE_250DPS = 131.0  # LSB pro deg/s bei +-250dps


class MPU6886:
    def __init__(self, i2c: I2C, address: int = 0x68):
        self.i2c = i2c
        self.address = address

        who_am_i = self.i2c.readfrom_mem(self.address, _REG_WHO_AM_I, 1)[0]
        if who_am_i not in (0x19, 0x69):  # 0x19 = MPU6886
            raise RuntimeError(f"Unerwartete WHO_AM_I 0x{who_am_i:02X} auf 0x{address:02X}")

        self.i2c.writeto_mem(self.address, _REG_PWR_MGMT_1, bytes([0x00]))  # aufwecken
        time.sleep_ms(10)
        self.i2c.writeto_mem(self.address, _REG_ACCEL_CONFIG, bytes([0x00]))  # +-2g
        self.i2c.writeto_mem(self.address, _REG_GYRO_CONFIG, bytes([0x00]))   # +-250dps
        time.sleep_ms(10)

    @staticmethod
    def _to_signed(hi, lo):
        v = (hi << 8) | lo
        return v - 65536 if v > 32767 else v

    def read(self):
        """Liefert dict mit accel_g (x,y,z), gyro_dps (x,y,z), temperature_c."""
        raw = self.i2c.readfrom_mem(self.address, _REG_ACCEL_XOUT_H, 14)

        ax = self._to_signed(raw[0], raw[1]) / _ACCEL_SCALE_2G
        ay = self._to_signed(raw[2], raw[3]) / _ACCEL_SCALE_2G
        az = self._to_signed(raw[4], raw[5]) / _ACCEL_SCALE_2G

        temp_raw = self._to_signed(raw[6], raw[7])
        temperature_c = temp_raw / 326.8 + 25.0

        gx = self._to_signed(raw[8], raw[9]) / _GYRO_SCALE_250DPS
        gy = self._to_signed(raw[10], raw[11]) / _GYRO_SCALE_250DPS
        gz = self._to_signed(raw[12], raw[13]) / _GYRO_SCALE_250DPS

        return {
            "accel_g": (round(ax, 3), round(ay, 3), round(az, 3)),
            "gyro_dps": (round(gx, 2), round(gy, 2), round(gz, 2)),
            "temperature_c": round(temperature_c, 2),
        }
