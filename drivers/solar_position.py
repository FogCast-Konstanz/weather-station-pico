"""
Vereinfachte Sonnenstandsberechnung (Elevation/Zenitwinkel) fuer MicroPython.
Wird genutzt, um die Rohwerte eines fest montierten UV-Sensors (AS7331) grob
um den Kosinus-Fehler zu korrigieren, der entsteht, weil der Sensor nicht
senkrecht zur Sonne steht (Sommer/Winter-Unterschied durch flacheren bzw.
steileren Sonnenstand).

WICHTIG - was das hier NICHT leistet:
- Keine Wetter-/Wolken-/Aerosolkorrektur, nur die reine Geometrie.
- Die reale Winkelantwort eines Sensors ist selten ein perfektes Kosinus,
  besonders am Rand (>70 deg Zenitwinkel). Fuer echte Messgenauigkeit
  braeuchtet ihr die tatsaechliche Winkel-Kennlinie aus dem AS7331-Datenblatt
  oder eine eigene Kalibrierung (Sensor auf Drehteller, Referenzlampe).
- Braucht eine halbwegs genaue Uhrzeit (UTC) und eure Standortkoordinaten.
  Der Pico 2 hat keine Echtzeituhr - entweder ueber NTP synchronisieren
  (nur mit Pico 2 W / WLAN) oder ein externes RTC-Modul (z.B. DS3231) an
  I2C1 mitbetreiben.

Formeln nach dem vereinfachten NOAA-Sonnenstandsalgorithmus (Standard-
Nherungsformeln, keine Bibliothekscode-Uebernahme).
"""
import math


def _day_of_year(year, month, day):
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        days_in_month[1] = 29
    return sum(days_in_month[:month - 1]) + day


def solar_elevation_deg(year, month, day, hour_utc, minute_utc, lat_deg, lon_deg):
    """Liefert die Sonnenelevation in Grad (0 = Horizont, 90 = Zenit, negativ = Nacht)."""
    n = _day_of_year(year, month, day)
    fractional_hour = hour_utc + minute_utc / 60.0

    # Deklination der Sonne (vereinfachte Naeherung)
    declination = 23.44 * math.sin(math.radians(360.0 / 365.0 * (n - 81)))

    # Zeitgleichung (vereinfachte Naeherung in Minuten)
    b = math.radians(360.0 / 365.0 * (n - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)

    # Wahre Ortszeit -> Stundenwinkel
    time_correction = 4 * lon_deg + eot  # Minuten
    solar_time = fractional_hour + time_correction / 60.0
    hour_angle = 15.0 * (solar_time - 12.0)  # Grad

    lat_rad = math.radians(lat_deg)
    dec_rad = math.radians(declination)
    ha_rad = math.radians(hour_angle)

    elevation_rad = math.asin(
        math.sin(lat_rad) * math.sin(dec_rad)
        + math.cos(lat_rad) * math.cos(dec_rad) * math.cos(ha_rad)
    )
    return math.degrees(elevation_rad)


def cosine_correction_factor(elevation_deg, min_elevation_deg=5.0):
    """
    Skaliert ein Rohsignal so hoch, wie es bei senkrechtem Sonnenstand waere.
    Unterhalb von min_elevation_deg (Sonne nah am Horizont) wird nicht mehr
    korrigiert, da der Fehler dort explodiert und die Naeherung unbrauchbar wird.
    """
    if elevation_deg < min_elevation_deg:
        return None  # Messung in diesem Bereich lieber verwerfen/als unsicher markieren
    zenith_rad = math.radians(90.0 - elevation_deg)
    return 1.0 / math.cos(zenith_rad)


def correct_uv_reading(raw_value, year, month, day, hour_utc, minute_utc, lat_deg, lon_deg):
    """Beispiel-Verwendung: korrigiert einen rohen AS7331-Zaehlwert um den Sonnenstand."""
    elevation = solar_elevation_deg(year, month, day, hour_utc, minute_utc, lat_deg, lon_deg)
    factor = cosine_correction_factor(elevation)
    if factor is None:
        return None, elevation
    return raw_value * factor, elevation
