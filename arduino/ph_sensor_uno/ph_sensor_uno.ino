/*
=====================================================
            AquaSentinel AI
        Arduino Uno - pH + Temperature
-----------------------------------------------------
Reads the analog pH sensor (A0) and an analog
temperature sensor (LM35 on A1, optional) and prints
one clean line per reading over Serial:

        PH:7.24 TEMP:26.5

The laptop (serial_reader.py) parses exactly this line.
The NodeMCU can also read this line and relay it over
Wi-Fi. Python does NOT control the Arduino -- the
Arduino just reads and reports.

Wiring:
  pH sensor analog out  -> A0
  LM35 Vout             -> A1   (skip if you have no temp sensor)
  Both sensors          -> 5V and GND
=====================================================
*/

const int PH_PIN   = A0;
const int TEMP_PIN = A1;      // LM35; comment out temp block if unused
const float VREF   = 5.0;     // Uno ADC reference voltage

// --- pH calibration (replace after calibrating with buffer solutions) ---
// pH = 7 at the sensor's neutral voltage; slope from a 2-point calibration.
const float PH_NEUTRAL_V = 2.5;
const float PH_SLOPE     = 0.18;  // volts per pH unit (approx; calibrate!)

float readPH() {
  int raw = analogRead(PH_PIN);
  float voltage = raw * (VREF / 1023.0);
  float ph = 7.0 + ((PH_NEUTRAL_V - voltage) / PH_SLOPE);
  if (ph < 0)  ph = 0;          // clamp to the real pH scale
  if (ph > 14) ph = 14;
  return ph;
}

float readTempC() {
  // LM35: 10 mV per degree C.
  int raw = analogRead(TEMP_PIN);
  float voltage = raw * (VREF / 1023.0);
  return voltage * 100.0;
}

void setup() {
  Serial.begin(9600);
  Serial.println("AquaSentinel AI - Uno pH+Temp ready");
}

void loop() {
  float ph   = readPH();
  float temp = readTempC();

  // One machine-readable line the laptop / NodeMCU parses:
  Serial.print("PH:");
  Serial.print(ph, 2);
  Serial.print(" TEMP:");
  Serial.println(temp, 1);

  delay(1000);
}
