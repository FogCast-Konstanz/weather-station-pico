# Dokumentation FogCast UV- & weitere Sensoren

## 1. Einleitung und Projektziel
In meteorologischen und umwelttechnischen Messstationen ist die präzise Erfassung von Umweltparametern essenziell[cite: 17]. Ziel dieses Projekts war der Aufbau einer autarken Wetterstation auf Basis eines Raspberry Pi Pico 2[cite: 17]. Neben Standardparametern wie Temperatur, Luftfeuchtigkeit und Luftdruck stand insbesondere die Erfassung der solaren UV-Strahlung und die Ableitung eines standardisierten UV-Index im Fokus[cite: 17]. Das Projekt durchlief typische Phasen der Embedded-Entwicklung: von der Sensorauswahl über Hardware-Architektur, optische Herausforderungen und Kalibrierung bis hin zur Treiberentwicklung in MicroPython[cite: 17].

## 2. Sensoren - Übersicht
Alle Sensoren kommunizieren digital über den I²C-Bus[cite: 17]. Um Adresskonflikte zu umgehen und Signallaufzeiten sauber zu trennen, wurde das System in vier getrennte I²C-Busse aufgeteilt[cite: 17]:

| Sensor-Baugruppe | Messgrößen | Bus-Typ / Zuordnung | I²C-Adresse |
| :--- | :--- | :--- | :--- |
| **SHT30 (intern)** | Gehäusetemperatur, Luftfeuchte | Hardware I2C (0) (GP8/GP9) | `0x44`[cite: 17] |
| **QMP6988** | Luftdruck, Chiptemperatur | Hardware I2C (0) (GP8/GP9) | `0x70`[cite: 17] |
| **SHT30 (extern)** | Außentemperatur, Luftfeuchte | Hardware I2C (1) (GP6/GP7) | `0x44`[cite: 17] |
| **MPU6886 (IMU)** | Beschleunigung, Drehrate | Soft I2C an Port A2 (GP28) | `0x68`[cite: 17] |
| **AS7331** | UVA-, UVB-, UVC-Strahlung | Soft I2C an Port D20 (GP20) | `0x74`[cite: 17] |

Zur Ermittlung der Sekundär-Pins für die softwarebasierten Busse (Bit-Banging) kam das hardwarenahe Diagnose-Skript `i2c_pin_scan.py` zum Einsatz, welches die Grove-Pins automatisiert abtastet[cite: 17].

## 3. System- und Busarchitektur

### 3.1 AS7331 Spektraler 3-Kanal-UV-Strahlungssensor
* **Funktionsweise:** Der optische Sensor misst über drei getrennte Photodioden-Arrays mit Interferenzfiltern die Bereiche UVA (315-410 nm), UVB (280-315 nm) und UVC (200-280 nm)[cite: 17].
* **Registerarchitektur:** Der Chip unterscheidet strikt zwischen einem Konfigurationsmodus (`_OSR_SS_CONFIG`) zur Einstellung von Integrationszeit und Verstärkung sowie dem Messmodus (`OSR_SS_START_MEASURE`) zum Triggern von Einzel- oder Dauermessungen[cite: 17].
* **Auslesung:** Die spektralen Energieflüsse werden als vorzeichenlose 16-Bit-Rohzählwerte über getrennte Ergebnisregister (`MRES1` bis `MRES3`) ausgelesen[cite: 17].

### 3.2 SHT30 - Digitaler Feuchte- und Temperatursensor (Intern & Extern)
* **Funktionsweise:** Der kapazitive Feuchtesensor und Bandabstands-Temperatursensor wandelt physikalische Werte intern über ADCs mit hoher Wiederholgenauigkeit um[cite: 17].
* **Signalverarbeitung:** Die Messung wird über den Befehl `0x2400` (Single-Shot, High Repeatability) getriggert[cite: 17].
* **Fehlererkennung:** Die 6-Byte-Rückgabe (jeweils 2 Byte Messwert + 1 Byte CRC8-Prüfsumme nach dem Polynom $x^8+x^5+x^4+1$) wird im Treiber verifiziert[cite: 17]:
  $$T=-45+175\cdot\frac{S_{T}}{2^{16}-1}, \quad RH=100\cdot\frac{S_{RH}}{2^{16}-1}$$[cite: 17]

### 3.3 QMP6988 - Piezoresistiver Absolut-Luftdrucksensor
* **Funktionsweise:** Sitzt als Kombi-Chip auf dem internen Modul und misst den Atmosphärendruck über eine piezoresistive Silizium-Membran[cite: 17].
* **Kompensation:** Der Rohdruck wird als 24-Bit-Wert bezüglich des Nullpunkts $2^{23}$ erfasst[cite: 17]. Ein herstellerspezifisches Polynom 3. Grades verrechnet 25 werkseitig ausgelesene Kalibrierkoeffizienten mit der Chiptemperatur zur exakten Druckbestimmung in hPa[cite: 17].

### 3.4 MPU6886 - 6-Achsen-Inertialmesseinheit (IMU)
* **Funktionsweise:** Kombiniert ein 3-Achsen-MEMS-Gyroskop (±250°/s) mit einem 3-Achsen-MEMS-Beschleunigungssensor (±2g)[cite: 17].
* **Zweck im Aufbau:** Dient der kontinuierlichen Überprüfung der horizontalen Ausrichtung des Gehäusedeckels zur Vermeidung von Messfehlern bei der Einstrahlung[cite: 17].
* **Auslesung:** Die 14 Register ab `0x3B` liefern synchron 16-Bit-Zweierkomplement-Werte für alle sechs Achsen sowie die Sensortemperatur[cite: 17].

## 4. Physikalische Herausforderungen und Kalibrierung der UV-Messung

### 4.1 Die Material-Barriere: UV-Transmission
Herkömmliches Fensterglas, Bilderrahmenglas oder Standard-Acrylglas blockt UV-B-Strahlung physikalisch zu nahezu 100%[cite: 17]. In Testreihen führte eine gewöhnliche Glasabdeckung zu einem Einbruch der UVB-Rohwerte auf 0.00[cite: 17]. Für wettergeschützte Gehäuseöffnungen entschied sich das Team für den Einsatz von hochgradig UV-durchlässigem **Saphirglas** (Transmission von 200 bis 5500 nm), um die Erfassung der UV-A (320-400 nm) und UV-B (280-320 nm) Strahlungen sicherzustellen[cite: 17].

### 4.2 Berechnung des UV-Index
Da der internationale UV-Index primär auf der erythemwirksamen (sonnenbrandverursachenden) Strahlungsfunktion basiert, trägt UVB exponentiell stärker bei als UVA[cite: 17]. Im Treiber wird der UV-Index aus den Rohzählern synthetisiert[cite: 17]:
$$\text{UVI}_{\text{raw}} = (\text{UVB}_{\text{raw}} \cdot 1.0 + \text{UVA}_{\text{raw}} \cdot 0.001) \cdot k_{\text{cal}}$$[cite: 17]
Unter wolkenfreier Referenzstrahlung mit einem Ziel-Index von 5.5 wurde der Kalibrierungsfaktor für den unbedeckten Sensor auf $k_{cal}=0.077$ bestimmt[cite: 17]. Das Ergebnis wird im Treiber direkt auf eine ganzzahlige Stufe gerundet[cite: 17].

### 4.3 Geometrische Sonnenstand Korrektur
Ein statisch horizontal montierter Sensor unterliegt bei tief stehender Sonne dem Lambertschen Kosinusgesetz: Die projizierte Empfängerfläche verringert sich mit flacher werdendem Einstrahlwinkel[cite: 17]. 
Im Modul `solar_position.py` wird basierend auf Standortkoordinaten (Breiten-/Längengrad) und UTC-Zeit die astronomische Sonnenhöhe ($\gamma_S$) berechnet[cite: 17]:
$$\text{Korrekturfaktor} = \frac{1}{\cos(90^\circ - \gamma_S)} = \frac{1}{\sin(\gamma_S)}$$[cite: 17]
Das Hauptprogramm skaliert die Messwerte für Sonnenstände $\ge 5^\circ$ Elevation hoch, wodurch winkelbedingte Abschattungsverluste rechnerisch korrigiert werden[cite: 17].

## 5. Software-Ablauf und Zustandssteuerung
Das Hauptprogramm arbeitet nicht-blockierend über `time.ticks_ms()`-Zeitdifferenzen, um Bus-Blockaden zu verhindern[cite: 17]. 
* **Fehlertoleranz:** Über `safe_init()` wird jeder Sensor gekapselt initialisiert[cite: 17]. Der Ausfall eines Sensors bringt nicht das gesamte System zum Absturz[cite: 17].
* **Phasen-Umschaltung:** Über `config.py` lässt sich das System zwischen einer Testphase (5 Sekunden Takt) und der regulären Betriebsphase (300 Sekunden Takt) umschalten, ohne Programmlogik anzupassen[cite: 17].

## 6. Anhang: Sonnenposition & Korrektur

### Lambertsches Kosinusgesetz
Ein paralleles Lichtbündel trifft auf eine geneigte Fläche $A_s$. Geometrisch gilt:
$$A_s = \frac{A_\perp}{\cos(\theta)}$$[cite: 17]
Die Bestrahlungsstärke verteilt sich auf die größere Fläche $A_s$, woraus sich für den Sensor ergibt[cite: 17]:
$$E_{\text{Sensor}} = E_\perp \cdot \cos(\theta)$$[cite: 17]

### Solare Zenitwinkel & Jahreszeiten
Der Kosinussatz der sphärischen Trigonometrie liefert den solaren Zenitwinkel ($\theta_z$)[cite: 17]:
$$\cos(\theta_z) = \sin(\varphi)\sin(\delta) + \cos(\varphi)\cos(\delta)\cos(h)$$[cite: 17]
Durch die Neigung der Erdachse pendelt die Deklination ($\delta$) im Jahresverlauf sinusförmig[cite: 17]:
$$\delta(n) \approx \epsilon \cdot \sin\left(\frac{360^\circ}{365}(n-81)\right)$$[cite: 17]
Das führt dazu, dass ein flach montierter Sensor die UV-Strahlung im Winter (hoher Zenitwinkel) rein durch die Sensorgeometrie deutlich stärker unterschätzt als im Sommer[cite: 17]. 

### Einschränkung der Korrektur
Der berechnete Kosinus-Faktor korrigiert lediglich den Messfehler des Sensors aufgrund seiner flachen Auflage (Fußabdruck-Effekt)[cite: 17]. Die physikalische atmosphärische Abschwächung (Luftmasse $\approx 1/\cos\theta_z$) durch Ozon und Aerosole wird hierdurch nicht korrigiert und dokumentiert die reale UV-Belastung[cite: 17].
