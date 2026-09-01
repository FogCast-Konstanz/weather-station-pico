# Hardware-Aufbau und Verkabelung

Das System basiert auf einer Multi-Bus-Architektur, um I²C-Adresskonflikte (z.B. zwei baugleiche SHT30-Sensoren auf `0x44`) zu vermeiden und die Systemstabilität zu maximieren[cite: 10, 12]. 

## 1. Die vier I²C-Busse

Das System nutzt 4 logisch und physisch getrennte Busse auf dem Raspberry Pi Pico 2:

| Bus | Grove-Port | Sensoren | I²C-Adresse |
| :--- | :--- | :--- | :--- |
| **Hardware I²C(0)** | `I2C0` | SHT30 (intern) + QMP6988 (Kombi-Board)[cite: 10] | `0x44` / `0x70`[cite: 12, 13] |
| **Hardware I²C(1)** | `I2C1` | SHT30 (extern, Mesh-geschützt)[cite: 10] | `0x44`[cite: 12] |
| **Software I²C** | `A2` | MPU6886 (IMU)[cite: 10] | `0x68`[cite: 14] |
| **Software I²C** | `D20` | AS7331 (UV-Sensor)[cite: 10] | `0x74`[cite: 15] |

## 2. Physische Verkabelung (Qwiic-System)

Aufgrund der Verwendung von Sensoren mit nur einem einzelnen Qwiic-Anschluss ("Sackgassen-Sensoren") ist kein simples Daisy-Chaining möglich.

* **Bus 1 (I2C0):** Ein Qwiic-zu-Jumper-Kabel verbindet den Pico 2 mit einem **Qwiic MultiPort Hub** ("I²C-Verteiler"). Von diesem Hub führt ein einzelnes Qwiic-Kabel zum internen SHT30/QMP6988-Kombi-Board.
* **Bus 2 (I2C1):** Der externe SHT30 (Adafruit) wird über ein eigenes Qwiic-zu-Jumper-Kabel direkt an die Pins des zweiten Hardware-Busses angeschlossen[cite: 10].
* **Bus 3 & 4 (A2 & D20):** IMU und UV-Sensor werden per Grove-Stecker oder direkter Pin-Verkabelung an die zugewiesenen SoftI²C-Pins angebunden[cite: 10].

## 3. Besonderheiten beim Gehäuseaufbau

### Sensorausrichtung (IMU & UV)
Der optische UV-Sensor AS7331 misst die Bestrahlungsstärke auf eine horizontale Fläche. Er muss zwingend exakt waagerecht montiert werden[cite: 16]. Die verbaute MPU6886 (IMU) dient der Ausrichtungskontrolle[cite: 14].

### UV-Transmission
Der AS7331 sitzt unter dem Deckel des Holzgehäuses. **Wichtig:** Das Sichtloch darf nicht mit gewöhnlichem Fensterglas oder Standard-Plexiglas abgedeckt werden, da dies UV-B-Strahlung zu 100 % absorbiert. Es muss zwingend **Quarzglas, FEP-Folie oder spezielles UV-durchlässiges Acrylglas (z.B. Plexiglas Sun)** verwendet werden, andernfalls misst der Sensor permanent `0.00 UVB`.

```
