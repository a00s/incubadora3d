#include <Arduino.h>
#include <SoftwareSerial.h>     
#include <SPI.h>
#include "Ucglib.h"
#include "display_font.h"
#include <NDIRZ16.h>
#include <avr/wdt.h>
#include <EEPROM.h>
#include <avr/pgmspace.h>
#include <string.h>

#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>
#include <OneWire.h>

//#define ERROR_LOG_ADDRESS 0 // EEPROM address to store error log
#define EEPROM_CONTADOR 24
#define EEPROM_CO2_RANGE_LOCK 28
#define EEPROM_CONTROL_STATE 29
#define EEPROM_SAFETY_FAULT 30

#define CHAMBER_TEMPERATURE_PIN 4
#define DHT_TEMPERATURA_INT_PIN 2
#define DHTTYPE DHT22

OneWire chamberOneWire(CHAMBER_TEMPERATURE_PIN);
uint8_t chamberSensorAddress[8];
bool chamberSensorFound = false;
float chamberTemperatureC = NAN;
unsigned long chamberConversionStartedAt = 0;

void startChamberConversion() {
  if (chamberOneWire.reset()) {
    chamberOneWire.select(chamberSensorAddress);
    chamberOneWire.write(0x44); // Convert T; external 5 V supply, no parasite mode.
  }
  chamberConversionStartedAt = millis();
}

void beginChamberTemperature() {
  chamberConversionStartedAt = millis();
  // Read ROM is intentionally limited to one sensor on this bus.
  if (!chamberOneWire.reset()) return;
  chamberOneWire.write(0x33);
  for (uint8_t i = 0; i < 8; i++) chamberSensorAddress[i] = chamberOneWire.read();
  chamberSensorFound = chamberSensorAddress[0] == 0x28 &&
    OneWire::crc8(chamberSensorAddress, 7) == chamberSensorAddress[7];
  if (!chamberSensorFound) return;
  chamberOneWire.reset();
  chamberOneWire.select(chamberSensorAddress);
  chamberOneWire.write(0x4E); // Write scratchpad, without writing sensor EEPROM.
  chamberOneWire.write(0); // Alarm TH (unused).
  chamberOneWire.write(0); // Alarm TL (unused).
  chamberOneWire.write(0x7F); // 12-bit resolution.
  startChamberConversion();
}

// Do not block relay servicing during the DS18B20's 750 ms conversion.
void serviceChamberTemperature() {
  if (!chamberSensorFound) {
    chamberTemperatureC = NAN;
    if (millis() - chamberConversionStartedAt >= 2000UL) beginChamberTemperature();
    return;
  }
  if (millis() - chamberConversionStartedAt < 800UL) return;
  chamberTemperatureC = NAN;
  if (chamberOneWire.reset()) {
    chamberOneWire.select(chamberSensorAddress);
    chamberOneWire.write(0xBE); // Read scratchpad including CRC.
    uint8_t scratch[9];
    for (uint8_t i = 0; i < 9; i++) scratch[i] = chamberOneWire.read();
    int16_t raw = (int16_t)((uint16_t)scratch[1] << 8 | scratch[0]);
    // Configuration check rejects all-zero responses and unexpected resolution settings.
    // 85 C is the power-on value; never use it as a control measurement.
    if (OneWire::crc8(scratch, 8) == scratch[8] && scratch[4] == 0x7F &&
        raw >= -880 && raw <= 2000 && raw != 1360) {
      chamberTemperatureC = raw / 16.0f;
    }
  }
  startChamberConversion();
}
DHT dhtint(DHT_TEMPERATURA_INT_PIN, DHTTYPE);

#define HEATER 6
#define CO2PUMP 7
#define BOTAO_CO2 1
#define BOTAO_AQUECEDOR 0
#define BAUDRATE 9600                                      // Device to MH-Z19 Serial baudrate (should not be changed)

#define CO2_TARGET_PPM 50000L
#define CO2_TOLERANCE_PPM 1000L
#define CO2_DISPLAY_NEAR_TOLERANCE_PPM 5000L
#define CO2_CONTROL_MIN_PPM (CO2_TARGET_PPM - CO2_TOLERANCE_PPM)
#define CO2_CONTROL_MAX_PPM (CO2_TARGET_PPM + CO2_TOLERANCE_PPM)
#define CO2_SENSOR_PROTOCOL_MAX_PPM 65535L
#define CO2_SENSOR_LOCK_PPM 60000L
#define CO2_SENSOR_LOCK_MAGIC 0xA5
#define CO2_SENSOR_WARMUP_MS 120000UL
#define CO2_GOOD_MIN_PPM CO2_CONTROL_MIN_PPM
#define CO2_MAX_RISING_RATE_PPM_PER_MIN 300L
#define CO2_STABLE_TIME_MS 30000UL
#define CO2_RESPONSE_LAG_DEFAULT_MS 120000UL
#define CO2_RESPONSE_LAG_MIN_MS 90000UL
#define CO2_RESPONSE_LAG_MAX_MS 180000UL
// Sensor readings remain uncorrected.
#define HEATER_SETPOINT_C 37.0
#define HEATER_MIN_OFF_MS 3000UL
#define HEATER_PID_MAX_ON_MS 12000UL
#define HEATER_TREND_WINDOW_MS 30000UL
#define HEATER_PID_KP_MS_PER_C 18000.0f
#define HEATER_PID_KI_MS_PER_C_MIN 5000.0f
#define HEATER_PID_KD_MS_PER_C_MIN 6000.0f
#define HEATER_HARD_CUTOFF (HEATER_SETPOINT_C + 0.1)
#define HEATER_EMERGENCY_CUTOFF 39.0
#define TEMPERATURE_GOOD_MIN (HEATER_SETPOINT_C - 0.1)
#define TEMPERATURE_GOOD_MAX (HEATER_SETPOINT_C + 0.1)
#define TEMPERATURE_DISPLAY_NEAR_MIN (HEATER_SETPOINT_C - 0.5)
#define TEMPERATURE_DISPLAY_NEAR_MAX (HEATER_SETPOINT_C + 0.5)
#define POMP_WAITING_TIME 30 // Cerca de 1 minuto com o ciclo atual de 2 s para o MH-Z perceber o pulso
#define MAX_INTERNAL_TEMP 31 // Liga fan acima de 31 C; desliga abaixo de 30 C

#define VENTILADOR_PIN 3

SoftwareSerial mySerialCO2(12,5);
NDIRZ16 mySensorCO2 = NDIRZ16(&mySerialCO2);
Ucglib_ST7735_18x128x160_HWSPI ucg(/*cd=*/ 9, /*cs=*/ 10, /*reset=*/ 8);

bool botao_co2_onoff = false;
bool botao_aquecedor_onoff = false;
int32_t last_co2i = 0;
uint8_t contador_pomp;
int32_t CO2i = 0;
int32_t lastCo2RawPpm = 0;
uint16_t lastCo2PulseMs = 0;
int32_t eeprom_contador_int = 0;
bool ventilador_status = false;
unsigned long heaterPidLastUpdateAt = 0;
unsigned long heaterLastTransitionAt = 0;
unsigned long heaterSensorFaultSince = 0;
unsigned long heaterPulseStartedAt = 0;
uint16_t heaterCurrentPulseMs = 0;
unsigned long heaterTrendReferenceAt = 0;
float heaterTrendReferenceC = 0.0f;
float heaterTempRateCPerMin = 0.0f;
float heaterPidIntegralMs = 0.0f;
uint16_t heaterPidDemandMs = 0;
bool heaterPidInitialized = false;
bool heaterTrendReady = false;
bool co2ReferenceReady = false;
bool co2BaselineReady = false;
bool co2TrendReady = false;
bool serialHeaderPrinted = false;
bool lastCo2ReadingValid = false;
bool co2RangeWrapLatched = false;
bool co2RawReferenceReady = false;
bool displayCacheValid = false;
int32_t displayCo2Ppm = -2;
int8_t displayCo2Quality = -1;
int8_t displayTempQuality = -1;
int8_t displayCo2RangeLock = -1;
int8_t displaySafetyAlert = -1;
uint8_t safetyFault = 0;
int16_t displayTempTenths = 32767;
int16_t displayInternalTempTenths = 32767;
int32_t displayLossCm3Hour = -2;
int8_t displayLossStable = -1;
int8_t displayLossHeld = -1;
bool displayAlert = false;
int8_t displayDoorMode = -1;
int8_t displayCo2Enabled = -1;
int8_t displayHeaterEnabled = -1;
int8_t displayFanOn = -1;
int8_t displayCo2Active = -1;
int8_t displayHeaterActive = -1;
uint8_t activityIconFrame = 0;
unsigned long lastActivityIconFrameAt = 0;
unsigned long co2AnimationUntil = 0;
int32_t displayCo2RatePpmMin = 0;
int8_t displayCo2RateReady = -1;
unsigned long lastValidCo2Time = 0;
unsigned long co2StableSince = 0;
char serialCommandBuffer[24];
uint8_t serialCommandLength = 0;
bool co2ButtonStable = false, co2ButtonCandidate = false;
bool heaterButtonStable = false, heaterButtonCandidate = false;
uint8_t co2ButtonDebounceCount = 0, heaterButtonDebounceCount = 0;
uint8_t co2ClickCount = 0;
bool co2ModeAtClickSequence = false;
unsigned long co2ClickSequenceStart = 0;
uint8_t heaterClickCount = 0;
unsigned long heaterClickSequenceStart = 0;
bool bothButtonsStable = false;
bool heaterPressPending = false;
unsigned long heaterPressedAt = 0;

// Variáveis para calcular a taxa de aumento de CO2
float co2Rate = 0; // Armazena a taxa de aumento do CO2
float maxRate = 0;
int32_t co2_before_pump = 0;
int32_t max_co2_increase = 0;
// Limites de taxa e delay para liberacao da valvula de CO2 proporcional a pressao
// analise: 1436ppm/s pra 0.5kg/cm2 com a valvula aperta por 5ms
const float TAXA_MAXIMA = 1000.0; // ppm/s
const float TAXA_MINIMA = 10.0;   // ppm/s
const int DELAY_MAXIMO = 80;     // ms; limita o pulso enquanto a resposta da válvula se adapta
const int DELAY_MINIMO = 20;      // ms; pulsos menores não geraram resposta confiável da válvula
const int32_t CO2_INITIAL_GAIN_ESTIMATE_X100 = 1200L; // Só prior; recalibrado pela primeira resposta
const int32_t CO2_MIN_GAIN_ESTIMATE_X100 = 50; // Evita divisão por zero: 0,5 ppm/ms
const int MANUAL_CO2_PULSE_MS = 5; // Pulso curto já citado como referência experimental
const int MANUAL_CO2_MAX_PULSE_MS = 20;
#define DISPLAY_FAULT 0
#define DISPLAY_WAIT 1
#define DISPLAY_READY 2
int8_t displayHealthState = DISPLAY_WAIT;
int32_t co2GainEstimatePpmPerMsX100 = CO2_INITIAL_GAIN_ESTIMATE_X100;
bool co2DoseResponsePending = false;
bool co2GainValidatedThisBoot = false;
bool co2LastResponseWeak = false;
unsigned long co2LastPulseAt = 0;
unsigned long co2MaxRiseAt = 0;
uint8_t co2ResponseLagSeconds = CO2_RESPONSE_LAG_DEFAULT_MS / 1000UL;
int32_t co2ProjectedPpm = 0;
// const float fatorProximidade = 0.01; // Ajuste este fator para calibrar o impacto da proximidade

// Janela para calcular a tendência de CO2 em ppm/min
unsigned long lastMinuteTime = 0; // Armazena o tempo do último cálculo de média
const unsigned long oneMinuteInterval = 60000; // Intervalo de um minuto em milissegundos
int32_t co2RatePpmMin = 0;
const uint8_t CO2_RATE_HISTORY_SIZE = 16;
int32_t co2RateHistoryPpm[CO2_RATE_HISTORY_SIZE];
unsigned long co2RateHistoryTime[CO2_RATE_HISTORY_SIZE];
uint8_t co2RateHistoryCount = 0;
uint8_t co2RateHistoryNext = 0;
bool co2RatePpmMinReady = false;

// Nominal CAD gas envelope: chamber 1576 + mixer 274 cm3.
// Contents displace gas: this is an estimate, not a calibrated leak flow meter.
const uint16_t CO2_GAS_VOLUME_CM3 = 1850;
bool lossFresh = false;
int32_t lossCm3HourX10 = -1;
bool lossStable = false;
unsigned long lossStartAt = 0;
uint16_t lossStartPpm = 0;
float lossDropTotal = 0, lossTimeTotal = 0;
uint16_t lossSegmentDrop = 0;
unsigned long lossSegmentMs = 0;
uint8_t lossWindows = 0;
// Door: 0 normal, 2 open, 3 recovering, 4 first recovery dose pending.
uint8_t co2DoorMode = 0;
// Enable requests captured before the door pause (CO2 bit 0, heater bit 1).
uint8_t doorResumeControls = 0;

// Variáveis globais para aprendizado adaptativo
// float media_eficiencia = 0.0;
// int contagem_aberturas = 0;

void updateDoorState(bool valid) {
  if (valid && co2DoorMode >= 3 && CO2i >= CO2_CONTROL_MIN_PPM) co2DoorMode = 0;
}

bool co2ResponseWaitComplete(unsigned long now) {
  // Confirmed decline below the good band can replenish after the minimum
  // cooldown; a rise or near-target reading retains the learned response wait.
  uint8_t seconds = CO2i < CO2_CONTROL_MIN_PPM && co2RatePpmMin < -50
    ? 60 : co2ResponseLagSeconds;
  return now - co2LastPulseAt >= (unsigned long)seconds * 1000UL;
}

void setup()
{  
    Serial.begin(9600);                                     // Device to serial monitor feedback

    // -------------------- DEBUG --------------------------

    co2RangeWrapLatched = EEPROM.read(EEPROM_CO2_RANGE_LOCK) == CO2_SENSOR_LOCK_MAGIC;
    uint8_t savedSafetyFault = EEPROM.read(EEPROM_SAFETY_FAULT);
    safetyFault = savedSafetyFault == 0xC1 ? 1 : (savedSafetyFault == 0xC2 ? 2 : 0);
    mySensorCO2.rawLoggingEnabled = co2RangeWrapLatched;
    uint8_t controlState = EEPROM.read(EEPROM_CONTROL_STATE);
    if (controlState <= 31) {
      botao_co2_onoff = controlState & 0x01;
      botao_aquecedor_onoff = (controlState >> 1) & 0x01;
      if (controlState & 4) {
        co2DoorMode = 2;
        doorResumeControls = (controlState >> 3) & 3;
        botao_co2_onoff = botao_aquecedor_onoff = 0;
      }
    }
    // A persisted range fault always overrides a saved CO2 enable request.
    if (co2RangeWrapLatched) botao_co2_onoff = 0;
    EEPROM.get(EEPROM_CONTADOR, eeprom_contador_int);
    eeprom_contador_int++;
    EEPROM.put(EEPROM_CONTADOR, eeprom_contador_int);
    Serial.print(F("BOOT_COUNT,"));
    Serial.println(eeprom_contador_int);
    if (co2RangeWrapLatched) Serial.println(F("EVENT,co2_range_lock_restored_after_boot"));
   
    
    // Check if there's an error log
//    char error[50];
//    EEPROM.get(ERROR_LOG_ADDRESS, error);
//    error[49] = '\0';  // Ensure null-termination
//    if (strlen(error) > 0) {
//      Serial.print("Previous error: ");
//      Serial.println(error);
//      // Clear the error log
//      EEPROM.put(ERROR_LOG_ADDRESS, "");
//    }
   
    
    // -------------------------------------------
    mySerialCO2.begin(9600);
    beginChamberTemperature();
    dhtint.begin();
    pinMode(HEATER,OUTPUT);
    digitalWrite(HEATER,HIGH);
    pinMode(CO2PUMP,OUTPUT);
    digitalWrite(CO2PUMP,HIGH);

    pinMode(VENTILADOR_PIN,OUTPUT);
    digitalWrite(VENTILADOR_PIN,HIGH);

//    // Set SPI settings to full speed
    SPI.begin();
    SPI.beginTransaction(SPISettings(40000000, MSBFIRST, SPI_MODE0)); // 40 MHz is typically the highest SPI speed for Arduino

    
    ucg.begin(UCG_FONT_MODE_TRANSPARENT);
    ucg.setRotate180();
    contador_pomp = POMP_WAITING_TIME;
//    if (MCUSR & (1 << WDRF)) {
//      Serial.println("Watchdog reset detected.");
//      EEPROM.put(ERROR_LOG_ADDRESS, "Watchdog reset detected."); // Optionally log to EEPROM
//    }
    // Disable auto-calibration
  disableAutoCalibration();
  // Reveal live readings only after sensor warm-up and configuration.
  drawDisplayFrame();
  //   mySerialCO2.listen();
  //  // Disable auto-calibration
    // byte autoCalibOff[] = {0xFF, 0x01, 0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x86};
    // mySerialCO2.write(autoCalibOff, 9);

  //   // Wait for a response (optional, for debugging)
    // delay(500);
  //   while (mySerialCO2.available()) {
  //       byte response = mySerialCO2.read();
  //       Serial.print(response, HEX);
  //       Serial.print(" ");
  //   }
  //   Serial.println();
  //   // Check the auto-calibration status from the response
  //   if (response[1] == 0x79 && response[2] == 0x00) {
  //     Serial.println("Auto-calibration is disabled.");
  //   } else if (response[1] == 0x79 && response[2] == 0x01) {
  //     Serial.println("Auto-calibration is enabled.");
  //   } else {
  //     Serial.println("Unknown response.");
  //   }
    // Send the command to check auto-calibration status
    // byte checkAutoCalib[] = {0xFF, 0x01, 0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x86}; // Example command, may vary based on sensor documentation
    // mySerialCO2.write(checkAutoCalib, 9);

    // // Wait for a response
    // delay(500);
    // byte response[9];
    // int index = 0;
    // while (mySerialCO2.available() && index < 9) {
    //   response[index++] = mySerialCO2.read();
    // }

    // // Print the response
    // Serial.print("Response: ");
    // for (int i = 0; i < 9; i++) {
    //   Serial.print(response[i], HEX);
    //   Serial.print(" ");
    // }
    // Serial.println();

    // // Check the auto-calibration status from the response
    // if (response[1] == 0x79 && response[2] == 0x00) {
    //   Serial.println("Auto-calibration is disabled.");
    // } else if (response[1] == 0x79 && response[2] == 0x01) {
    //   Serial.println("Auto-calibration is enabled.");
    // } else {
    //   Serial.println("Unknown response.");
    // }
    // Clear the reset flags
    MCUSR = 0;
    // Enable the Watchdog Timer
    wdt_enable(WDTO_8S);
}

void printFixed(float value, uint8_t decimals) {
  if (isnan(value)) {
    Serial.print(F("nan"));
    return;
  }
  uint16_t scale = decimals == 2 ? 100 : 10;
  bool negative = value < 0;
  float magnitude = negative ? -value : value;
  uint32_t scaled = (uint32_t)(magnitude * scale + 0.5f);
  if (negative) Serial.write('-');
  Serial.print((unsigned long)(scaled / scale));
  Serial.write('.');
  uint16_t fraction = scaled % scale;
  if (decimals == 2 && fraction < 10) Serial.write('0');
  Serial.print((unsigned long)fraction);
}

void loop()
{
    wdt_reset(); // Reset the watchdog timer



//    if (Serial.available() > 0) {
//        String command = Serial.readStringUntil('\n');
//        command.trim(); // Remove any trailing newline characters
//
//        if (command.equals("reinitialize")) {
//            reinitializeScreen();
//        } else {
//            Serial.println("Unknown command");
//        }
//    }
//    
    
    int32_t sensorPpm = mySensorCO2.getppm();
    bool sensorReadOk = sensorPpm >= 0;
    if (sensorReadOk) {
      CO2i = sensorPpm;
      if (sensorPpm >= CO2_SENSOR_LOCK_PPM && !co2RangeWrapLatched) {
        co2RangeWrapLatched = true;
        mySensorCO2.rawLoggingEnabled = true;
        EEPROM.update(EEPROM_CO2_RANGE_LOCK, CO2_SENSOR_LOCK_MAGIC);
        setCo2Enabled(false);
        Serial.println(F("EVENT,co2_near_protocol_limit,auto_locked_persistently"));
      }
      if (millis() < CO2_SENSOR_WARMUP_MS) {
        lastCo2RawPpm = sensorPpm;
        co2RawReferenceReady = false;
      } else if (!co2RawReferenceReady) {
        // Treat the first post-warmup value as baseline; MH-Z16 may report 500 ppm at boot.
        lastCo2RawPpm = sensorPpm;
        co2RawReferenceReady = true;
      } else {
        int32_t rawCo2Jump = sensorPpm - lastCo2RawPpm;
        if (rawCo2Jump >= 15000 || rawCo2Jump <= -15000) {
          co2RangeWrapLatched = true;
          mySensorCO2.rawLoggingEnabled = true;
          EEPROM.update(EEPROM_CO2_RANGE_LOCK, CO2_SENSOR_LOCK_MAGIC);
          setCo2Enabled(false);
          Serial.print(F("EVENT,co2_protocol_jump_suspected,delta_ppm,"));
          Serial.print(rawCo2Jump);
          Serial.println(F(",control_locked_until_restart"));
        }
        lastCo2RawPpm = sensorPpm;
      }
    } else {
      CO2i = -1;
      Serial.println(F("EVENT,co2_sensor_read_failed"));
    }
    unsigned long currentTime = millis();
    int32_t co2Delta = 0;
    bool validCo2 = sensorReadOk && CO2i > 0 && CO2i <= CO2_SENSOR_PROTOCOL_MAX_PPM && !co2RangeWrapLatched;
    lastCo2ReadingValid = validCo2;
    int32_t previousCo2i = last_co2i;
    if (validCo2) {
      if (co2ReferenceReady) {
        unsigned long deltaTime = currentTime - lastValidCo2Time;
        co2Delta = CO2i - previousCo2i;
        if (deltaTime > 0) {
          co2Rate = co2Delta * 1000.0f / deltaTime;
          if (co2Rate > maxRate) maxRate = co2Rate;
        } else {
          co2Rate = 0;
        }
      } else {
        co2ReferenceReady = true;
        co2Rate = 0;
        co2StableSince = 0;
        co2TrendReady = false;
      }
      lastValidCo2Time = currentTime;
      co2RateHistoryPpm[co2RateHistoryNext] = CO2i;
      co2RateHistoryTime[co2RateHistoryNext] = currentTime;
      co2RateHistoryNext = (co2RateHistoryNext + 1) & (CO2_RATE_HISTORY_SIZE - 1);
      if (co2RateHistoryCount < CO2_RATE_HISTORY_SIZE) co2RateHistoryCount++;
      if (co2RateHistoryCount == CO2_RATE_HISTORY_SIZE) {
        uint8_t oldest = co2RateHistoryNext;
        unsigned long rateWindowMs = currentTime - co2RateHistoryTime[oldest];
        if (rateWindowMs >= 30000UL) {
          int32_t ppmChange = CO2i - co2RateHistoryPpm[oldest];
          // Valid readings are limited to 65,535 ppm, so scaling by 6,000
          // stays within signed 32-bit range while retaining ppm/min units.
          co2RatePpmMin = ppmChange * 6000L / (int32_t)(rateWindowMs / 10UL);
          co2RatePpmMinReady = true;
        }
      }
      // Use the rolling ~30 s slope to avoid stacking doses while CO2 is still
      // rising after a pulse. A falling level must remain dose-ready so the
      // controller can replace gas lost through leaks. Individual MH-Z16
      // samples jitter by several ppm, so don't gate on per-sample changes.
      bool co2RiseSlow = co2RatePpmMinReady &&
                         co2RatePpmMin <= CO2_MAX_RISING_RATE_PPM_PER_MIN;
      if (co2RiseSlow) {
        if (co2StableSince == 0) co2StableSince = currentTime;
        co2TrendReady = currentTime - co2StableSince >= CO2_STABLE_TIME_MS;
      } else {
        co2StableSince = 0;
        co2TrendReady = false;
      }
      if (lastMinuteTime == 0) lastMinuteTime = currentTime;
      if (currentTime - lastMinuteTime >= oneMinuteInterval && co2RatePpmMinReady) {
        Serial.print(F("CO2_RATE_PPM_MIN,"));
        Serial.println(co2RatePpmMin);
        lastMinuteTime = currentTime;
      }
      if (co2BaselineReady) {
        int32_t increaseSincePump = CO2i - co2_before_pump;
        // Learn from the actual net rise. Extrapolating a door-opening decline
        // beyond closure invents dose gain and biases later pulses too small.
        if (increaseSincePump > max_co2_increase) {
          max_co2_increase = increaseSincePump;
          co2MaxRiseAt = currentTime;
        }
      } else {
        co2_before_pump = CO2i;
        co2BaselineReady = true;
      }
    } else {
      co2Rate = 0;
      co2ReferenceReady = false;
      co2StableSince = 0;
      co2TrendReady = false;
      co2RateHistoryCount = 0;
      co2RateHistoryNext = 0;
      co2RatePpmMinReady = false;
    }
    // Keep the minimum cooldown, then wait for a sustained slowdown before
    // another automatic dose. Live telemetry showed the chamber response can
    // keep rising well beyond 60 s; dosing during that rise stacked pulses.
    bool responseWaitComplete = co2ResponseWaitComplete(currentTime);
    bool recoveryReady = co2DoorMode >= 3 && CO2i < CO2_CONTROL_MIN_PPM &&
      co2RatePpmMin <= CO2_MAX_RISING_RATE_PPM_PER_MIN &&
      (co2DoorMode == 4 || (co2RatePpmMinReady && co2RatePpmMin <= 0 &&
       currentTime - co2LastPulseAt >= 60000UL));
    bool doseResponseReady = validCo2 && (recoveryReady ||
      (responseWaitComplete && contador_pomp == 0 && co2TrendReady));
    co2ProjectedPpm = CO2i;
    if (validCo2 && co2DoorMode < 3 && co2RatePpmMinReady && co2RatePpmMin < 0) {
      int32_t boundedRate = co2RatePpmMin;
      if (boundedRate < -5000) boundedRate = -5000;
      int32_t projected = CO2i + boundedRate * co2ResponseLagSeconds / 60L;
      if (projected < 0) projected = 0;
      co2ProjectedPpm = projected;
    }
    int32_t pulseLimit = DELAY_MINIMO;
    int32_t co2Deficit = CO2_TARGET_PPM - co2ProjectedPpm;
    if (validCo2 && co2Deficit > 0) {
      // Scale the pulse cap with the remaining deficit. A broad ramp responds
      // faster during large deficits while still tapering near target; the
      // observed dose gain continues to adapt each cycle.
      pulseLimit += co2Deficit >> 4;
      if (pulseLimit > DELAY_MAXIMO) pulseLimit = DELAY_MAXIMO;
    }
    int32_t delayProporcional = validCo2
      ? calcularDelayProporcional(co2ProjectedPpm, CO2_TARGET_PPM, co2GainEstimatePpmPerMsX100, doseResponseReady, pulseLimit)
      : DELAY_MINIMO;

    
    serviceChamberTemperature();
    float h = NAN; // DS18B20 measures temperature only; do not display stale RH.
    float t = chamberTemperatureC;
    float t_interna = dhtint.readTemperature();      
    processSerialCommands();
    // Apply the heater safety cut before automatic CO2 dosing in this loop.
    controlHeater(t, millis());
    if (validCo2) last_co2i = CO2i;
    // Serial.println(t_interna);
    if(t_interna >= MAX_INTERNAL_TEMP && ventilador_status == 0){
      Serial.println(F("EVENT,fan,on"));
       digitalWrite(VENTILADOR_PIN,LOW);
       ventilador_status = 1;
    } else if (t_interna < (MAX_INTERNAL_TEMP - 1.0) && ventilador_status == 1){
      Serial.println(F("EVENT,fan,off"));
       digitalWrite(VENTILADOR_PIN,HIGH); 
       ventilador_status = 0;
    }

    if(sensorReadOk && CO2i == 0){
      Serial.println(F("EVENT,co2_zero_reading,invalid_for_control"));
    }
    
//    Serial.print("CONT: ");
//    Serial.print(eeprom_contador_int);
////    Serial.print("\tMEM: ");
////    Serial.print(freeMemory());
//    Serial.print("\tVolt: ");
//    long voltage = readVCC();
//    Serial.print(voltage / 1000.0);
//    Serial.print("\tBotao CO2: ");
//    Serial.print(botao_co2_status);    
//    Serial.print("\tPompa CO2: ");
//    Serial.print(botao_co2_onoff);
//    Serial.print("\tBotao Aquecer: ");    
//    Serial.print(botao_aquecedor_status);    
//    Serial.print("\tAquecer: ");
//    Serial.print(botao_aquecedor_onoff);    
//    Serial.print("\tCO2: ");
//    Serial.println(CO2i);  

    // Capture the falling trend before a replenishment pulse resets its state.
    updateDoorState(validCo2);
    updateCo2Loss(validCo2 && co2DoorMode == 0 && !heaterPressPending);
    if (validCo2 && currentTime >= CO2_SENSOR_WARMUP_MS &&
        // Start replenishing halfway into the allowed band. Waiting for the
        // lower edge and then dosing only a fraction of the deficit biased
        // the measured steady state below the 5% setpoint.
        co2ProjectedPpm < (CO2_TARGET_PPM - CO2_TOLERANCE_PPM / 2) &&
        botao_co2_onoff == 1 &&
        doseResponseReady && co2ClickCount == 0 && !heaterPressPending &&
        millis() - co2LastPulseAt >= 1000UL) {
      int32_t pulseMs;
      if (lastCo2PulseMs == 0) {
        // Calibrate from this valve/tank state before using learned gain.
        pulseMs = DELAY_MINIMO;
        Serial.print(F("EVENT,co2_probe,"));
      } else {
        if (co2DoseResponsePending && lastCo2PulseMs > 0) {
          // Ignore responses below 50 ppm, where sensor noise and leak-model
          // error dominate; larger responses update gain gradually. If a pulse
          // produces no measurable rise, the next probe steps up gradually
          // instead of repeating the same ineffective minimum pulse forever.
          if (max_co2_increase >= 50) {
            int32_t observedGainX100 = max_co2_increase * 100L / lastCo2PulseMs;
            co2GainEstimatePpmPerMsX100 =
              (co2GainEstimatePpmPerMsX100 + observedGainX100 * 2L) / 3L;
            co2GainValidatedThisBoot = true;
            co2LastResponseWeak = false;
          } else {
            co2LastResponseWeak = true;
          }
          if (co2GainEstimatePpmPerMsX100 < CO2_MIN_GAIN_ESTIMATE_X100) {
            co2GainEstimatePpmPerMsX100 = CO2_MIN_GAIN_ESTIMATE_X100;
          }
          if (max_co2_increase >= 50 && co2MaxRiseAt > co2LastPulseAt) {
            unsigned long observedLagMs = co2MaxRiseAt - co2LastPulseAt;
            if (observedLagMs < CO2_RESPONSE_LAG_MIN_MS) {
              observedLagMs = CO2_RESPONSE_LAG_MIN_MS;
            }
            if (observedLagMs > CO2_RESPONSE_LAG_MAX_MS) {
              observedLagMs = CO2_RESPONSE_LAG_MAX_MS;
            }
            uint8_t observedLagSeconds = (observedLagMs + 500UL) / 1000UL;
            co2ResponseLagSeconds = (co2ResponseLagSeconds * 2 + observedLagSeconds) / 3;
          }
          co2DoseResponsePending = false;
        }
        pulseMs = calcularDelayProporcional(co2ProjectedPpm, CO2_TARGET_PPM,
                                            co2GainEstimatePpmPerMsX100, true, pulseLimit);
        // Weak probes must escape the startup cap and keep adapting.
        if (!co2GainValidatedThisBoot || co2LastResponseWeak)
          pulseMs = lastCo2PulseMs + 20;
        Serial.print(F("EVENT,co2_pulse,"));
      }
      // First probe stays small; subsequent unvalidated probes grow gradually.
      if (pulseMs > pulseLimit) pulseMs = pulseLimit;
      if (pulseMs < DELAY_MINIMO) pulseMs = DELAY_MINIMO;
      co2_before_pump = CO2i;
      co2BaselineReady = true;
      lastCo2PulseMs = pulseMs;
      Serial.println(pulseMs);
      finishCo2Loss();
      if (co2DoorMode == 4) co2DoorMode = 3;
      digitalWrite(CO2PUMP, LOW);
      delay(pulseMs);
      digitalWrite(CO2PUMP, HIGH);
      co2AnimationUntil = millis() + 3000UL;
      co2DoseResponsePending = true;
      max_co2_increase = 0;
      co2LastPulseAt = millis();
      co2MaxRiseAt = co2LastPulseAt;

      co2StableSince = 0;
      co2TrendReady = false;
      contador_pomp = POMP_WAITING_TIME;
      maxRate = 0;
    } else {
      digitalWrite(CO2PUMP, HIGH);
    }

    renderDisplay(t, t_interna, validCo2);
    if (!serialHeaderPrinted) {
    Serial.println(F("DATA,ms,co2_ppm,co2_valid,temp_c,rh_pct,t_int_c,co2_enabled,heater_enabled,heater_on,fan_on,valve_open,next_pulse_ms,last_pulse_ms,rate_ppm_s,rate_ppm_min_valid,rate_ppm_min,max_rate_ppm_s,delta_ppm,dose_rise_ppm,wait_cycles,trend_ready,heater_pid_demand_ms,heat_rate_c_min,co2_range_lock,co2_proj_ppm"));
      serialHeaderPrinted = true;
    }
    Serial.print(F("DATA,")); Serial.print(currentTime); Serial.print(','); Serial.print(CO2i); Serial.print(','); Serial.print(validCo2 ? 1 : 0);
    Serial.print(','); printFixed(t, 2); Serial.print(','); printFixed(h, 1); Serial.print(','); printFixed(t_interna, 1);
    Serial.print(','); Serial.print(botao_co2_onoff); Serial.print(','); Serial.print(botao_aquecedor_onoff); Serial.print(',');
    Serial.print(digitalRead(HEATER) == LOW ? 1 : 0); Serial.print(','); Serial.print(ventilador_status); Serial.print(',');
    Serial.print(digitalRead(CO2PUMP) == LOW ? 1 : 0); Serial.print(','); Serial.print(delayProporcional); Serial.print(',');
    Serial.print(lastCo2PulseMs); Serial.print(',');
    printFixed(co2Rate, 2); Serial.print(','); Serial.print(co2RatePpmMinReady ? 1 : 0); Serial.print(','); Serial.print(co2RatePpmMin); Serial.print(',');
    printFixed(maxRate, 2); Serial.print(','); Serial.print(co2Delta); Serial.print(',');
    Serial.print(max_co2_increase); Serial.print(','); Serial.print(contador_pomp); Serial.print(','); Serial.print(co2TrendReady && contador_pomp == 0 ? 1 : 0); Serial.print(','); Serial.print(heaterPidDemandMs); Serial.print(','); printFixed(heaterTempRateCPerMin, 2); Serial.print(','); Serial.print(co2RangeWrapLatched ? 1 : 0); Serial.print(','); Serial.println(co2ProjectedPpm);

    if (contador_pomp > 0) contador_pomp--;
    serviceInputsForTwoSeconds();
    // delay(60000);
}



void reinitializeScreen() {
    ucg.begin(UCG_FONT_MODE_TRANSPARENT);
    ucg.setRotate180();
    drawDisplayFrame();
}

void setDisplayBackground() {
  ucg.setColor(0, displayAlert ? 160 : 8, displayAlert ? 8 : 18, displayAlert ? 12 : 30);
}

void setDisplayForeground(uint8_t r, uint8_t g, uint8_t b) {
  if (displayAlert) ucg.setColor(0, 255, 255, 255);
  else ucg.setColor(0, r, g, b);
}

void drawCo2Icon(uint8_t x, uint8_t y, bool enabled, bool flowing, uint8_t frame) {
  setDisplayBackground();
  ucg.drawBox(x - 2, y - 1, 25, 17);
  if (!enabled && !flowing) return;
  setDisplayForeground(enabled ? 75 : 105, enabled ? 195 : 130, enabled ? 255 : 150);
  if (!flowing) {
    ucg.drawCircle(x + 5, y + 5, 3, UCG_DRAW_ALL);
    ucg.drawCircle(x + 15, y + 2, 2, UCG_DRAW_ALL);
    ucg.drawCircle(x + 17, y + 12, 2, UCG_DRAW_ALL);
    ucg.drawLine(x + 8, y + 4, x + 13, y + 3);
    ucg.drawLine(x + 8, y + 7, x + 15, y + 10);
    return;
  }
  for (uint8_t bubble = 0; bubble < 3; bubble++) {
    uint8_t phase = (frame + bubble * 2) & 3;
    uint8_t bx = x + 3 + bubble * 7 + ((phase == 1 || phase == 2) ? 1 : 0);
    uint8_t by = y + 13 - phase * 3;
    ucg.drawCircle(bx, by, bubble == 1 ? 2 : 1, UCG_DRAW_ALL);
  }
}

void drawHeaterIcon(uint8_t x, uint8_t y, bool enabled, bool heating, uint8_t frame) {
  setDisplayBackground();
  ucg.drawBox(x - 1, y - 1, 23, 17);
  if (!enabled && !heating) return;
  uint8_t red = enabled ? 255 : 135;
  uint8_t green = enabled ? 145 : 120;
  uint8_t blue = enabled ? 55 : 135;
  if (heating && (frame & 1)) green = 185;
  setDisplayForeground(red, green, blue);
  int8_t sway = heating && (frame & 1) ? 2 : 0;
  ucg.drawLine(x + 10 + sway, y + 1, x + 15, y + 7);
  ucg.drawLine(x + 15, y + 7, x + 17, y + 11);
  ucg.drawLine(x + 17, y + 11, x + 14, y + 14);
  ucg.drawLine(x + 14, y + 14, x + 6, y + 14);
  ucg.drawLine(x + 6, y + 14, x + 3, y + 11);
  ucg.drawLine(x + 3, y + 11, x + 5, y + 7);
  ucg.drawLine(x + 5, y + 7, x + 8 + sway, y + 4);
  ucg.drawLine(x + 8 + sway, y + 4, x + 7, y + 9);
  ucg.drawLine(x + 7, y + 9, x + 10 + sway, y + 12);
  ucg.drawLine(x + 10 + sway, y + 12, x + 13, y + 8);
  ucg.drawLine(x + 13, y + 8, x + 10 + sway, y + 1);
}

void drawFanIcon(uint8_t x, uint8_t y, bool enabled, bool spinning, uint8_t frame) {
  setDisplayBackground();
  ucg.drawBox(x - 1, y - 1, 21, 17);
  setDisplayForeground(enabled ? 75 : 130, enabled ? 195 : 145, enabled ? 255 : 160);
  static const int8_t bladeX[12] PROGMEM = {0, 4, 6, 7, 6, 4, 0, -4, -6, -7, -6, -4};
  static const int8_t bladeY[12] PROGMEM = {-7, -6, -4, 0, 4, 6, 7, 6, 4, 0, -4, -6};
  int16_t cx = x + 9;
  int16_t cy = y + 7;
  uint8_t offset = spinning ? frame : 0;
  for (uint8_t blade = 0; blade < 3; blade++) {
    uint8_t index = (offset + blade * 4) % 12;
    int8_t dx = (int8_t)pgm_read_byte(&bladeX[index]);
    int8_t dy = (int8_t)pgm_read_byte(&bladeY[index]);
    ucg.drawLine(cx, cy, cx + dx, cy + dy);
    ucg.drawLine(cx + dx / 2, cy + dy / 2, cx + dx, cy + dy);
  }
  ucg.drawCircle(cx, cy, 2, UCG_DRAW_ALL);
}

void updateActivityIcons() {
  if (!displayCacheValid || co2DoorMode == 2) return;
  unsigned long now = millis();
  bool co2Flowing = digitalRead(CO2PUMP) == LOW ||
                    (co2AnimationUntil != 0 && (int32_t)(now - co2AnimationUntil) < 0);
  bool heating = digitalRead(HEATER) == LOW;
  bool fanSpinning = ventilador_status != 0;
  uint8_t co2Frame = activityIconFrame & 3;
  uint8_t heaterFrame = activityIconFrame & 3;
  uint8_t fanFrame = activityIconFrame % 12;
  if (co2Flowing || displayCo2Active != co2Flowing) {
    drawCo2Icon(11, 137, botao_co2_onoff, co2Flowing, co2Frame);
    displayCo2Active = co2Flowing;
  }
  if (heating || displayHeaterActive != heating) {
    drawHeaterIcon(53, 136, botao_aquecedor_onoff, heating, heaterFrame);
    displayHeaterActive = heating;
  }
  if (fanSpinning || displayFanOn != fanSpinning) {
    drawFanIcon(98, 137, fanSpinning, fanSpinning, fanFrame);
    displayFanOn = fanSpinning;
  }
}

void serviceActivityIconAnimation() {
  unsigned long now = millis();
  if (now - lastActivityIconFrameAt < 160UL) return;
  lastActivityIconFrameAt = now;
  activityIconFrame = (activityIconFrame + 1) % 12;
  updateActivityIcons();
}

void setHealthColor() {
  if (displaySafetyAlert || co2RangeWrapLatched || displayHealthState == DISPLAY_FAULT) setDisplayForeground(245, 65, 75);
  else if (displayHealthState == DISPLAY_WAIT) setDisplayForeground(255, 190, 45);
  else setDisplayForeground(50, 220, 125);
}

void drawHealthIndicator() {
  uint8_t fault = co2RangeWrapLatched || displaySafetyAlert;
  setDisplayBackground();
  ucg.drawBox(0, 0, ucg.getWidth(), 21);
  if (fault || displayHealthState == DISPLAY_FAULT) setDisplayForeground(245, 65, 75);
  else if (displayHealthState == DISPLAY_WAIT) setDisplayForeground(255, 190, 45);
  else setDisplayForeground(50, 220, 125);
  ucg.drawBox(2, 5, 5, 11);
  ucg.setFont(incubadora_font_7x13);
  setDisplayForeground(fault ? 255 : 130, fault ? 255 : 190, 215);
  ucg.setPrintPos(11, 14);
  if (displaySafetyAlert == 1) ucg.print(F("SENSOR FAIL"));
  else if (displaySafetyAlert == 2) ucg.print(F("TEMP TOO HOT"));
  else if (displaySafetyAlert == 3) ucg.print(F("TEMP LOST"));
  else ucg.print(co2RangeWrapLatched ? F("CO2 BLOQUEADO") :
                 (co2DoorMode >= 3 ? F("RECUPERANDO") : F("CO2 ppm")));
  if (!displaySafetyAlert) {
    char bootCountText[12];
    bootCountText[0] = 'R';
    ltoa(eeprom_contador_int, bootCountText + 1, 10);
    setDisplayForeground(230, 235, 240);
    ucg.setPrintPos(ucg.getWidth() - ucg.getStrWidth(bootCountText) - 5, 14);
    ucg.print(bootCountText);
  }
}

void drawDisplayFrame() {
  ucg.clearScreen();
  setDisplayBackground();
  ucg.drawBox(0, 0, ucg.getWidth(), ucg.getHeight());
  drawHealthIndicator();
  ucg.setFont(incubadora_font_7x13);
  setDisplayForeground(150, 200, 225);
  ucg.setPrintPos(5, 57); ucg.print(F("TEMP"));
  ucg.setPrintPos(66, 57); ucg.print(F("INT"));
  if (co2DoorMode == 2) {
    drawDoorNotice();
    displayCacheValid = false;
    return;
  }
  setDisplayForeground(130, 190, 215);
  ucg.setPrintPos(5, 101); ucg.print(F("ppm/min"));
  setDisplayForeground(150, 200, 225);
  ucg.setPrintPos(5, 120); ucg.print(F("cm3/h"));
  // Visible bounds: header 5..15, CO2 24..39, labels 48..56,
  // temperatures 65..74, line 83, rate 92..102, loss 111..119,
  // line 128, icons 137..151. Eight blank pixel rows between blocks.
  setDisplayForeground(45, 65, 82); ucg.drawHLine(8, 83, 112);
  setDisplayForeground(45, 65, 82); ucg.drawHLine(8, 128, 112);
  drawCo2Icon(11, 137, botao_co2_onoff, false, 0);
  drawHeaterIcon(53, 136, botao_aquecedor_onoff, false, 0);
  drawFanIcon(98, 137, ventilador_status, ventilador_status != 0, activityIconFrame % 12);
  displayCacheValid = false;
}

void formatTenths(int32_t value, char *text) {
  if (value == -32768) {
    strcpy_P(text, PSTR("--.- C"));
    return;
  }
  int32_t magnitude = value < 0 ? -(int32_t)value : value;
  char whole[12];
  ltoa(magnitude / 10, whole, 10);
  uint8_t index = 0;
  if (value < 0) text[index++] = '-';
  for (uint8_t i = 0; whole[i] != '\0'; i++) text[index++] = whole[i];
  text[index++] = '.';
  text[index++] = '0' + magnitude % 10;
  text[index++] = ' ';
  text[index++] = 'C';
  text[index] = '\0';
}

void formatPpmPerMinute(int32_t value, bool valid, char *text) {
  if (!valid) {
    strcpy_P(text, PSTR("---"));
    return;
  }
  if (value > 99999 || value < -99999) {
    ltoa(value / 1000, text, 10);
    strcat_P(text, PSTR("k"));
  } else if (value > 0) {
    text[0] = '+';
    ltoa(value, text + 1, 10);
  } else {
    ltoa(value, text, 10);
  }
}


void finishCo2Loss() {
  // Commit each observed interval once, before the next injection/rise.
  if (lossFresh) {
    lossDropTotal += lossSegmentDrop;
    lossTimeTotal += lossSegmentMs;
    if (lossWindows < 3) lossWindows++;
  }
  lossStartAt = 0;
  lossStable = lossFresh = false;
}

void updateCo2Loss(bool valid) {
  unsigned long now = millis();
  if (!valid || now < CO2_SENSOR_WARMUP_MS ||
      !co2RatePpmMinReady || co2RatePpmMin > 0) {
    finishCo2Loss();
    return;
  }
  if (!lossStartAt || CO2i > lossStartPpm) {
    finishCo2Loss();
    lossStartAt = now;
    lossStartPpm = CO2i;
  }
  unsigned long elapsed = now - lossStartAt;
  if (!elapsed) return;
  lossSegmentDrop = lossStartPpm - CO2i;
  lossSegmentMs = elapsed;
  float drop = lossDropTotal + lossSegmentDrop;
  float observedMs = lossTimeTotal + elapsed;
  // Ratio of sums: longer observed intervals carry proportionally more weight.
  lossCm3HourX10 = drop * (CO2_GAS_VOLUME_CM3 * 36.0f) / observedMs + 0.5f;
  lossFresh = true;
  // Evidence threshold, not a required duration of a measurement interval.
  lossStable = lossWindows >= 3 && drop >= 100;
}

void drawTextChanges(const char *next, uint8_t x, uint8_t baseline,
                     uint8_t fieldTop, uint8_t fieldHeight, uint8_t fieldWidth,
                     uint8_t fgR, uint8_t fgG, uint8_t fgB) {
  setDisplayBackground();
  ucg.drawBox(x - 1, fieldTop, fieldWidth, fieldHeight);
  setDisplayForeground(fgR, fgG, fgB);
  ucg.setPrintPos(x, baseline);
  ucg.print(next);
}

void drawDoorNotice() {
  setDisplayBackground(); ucg.drawBox(0, 83, 128, 77);
  setDisplayForeground(255, 190, 45);
  ucg.setFont(incubadora_font_7x13);
  ucg.setPrintPos(22, 97);
  ucg.print(F("PORTA ABERTA"));
  // Same chamber and right hinges; door leaf projects to the right.
  ucg.drawFrame(30, 106, 40, 45);
  ucg.drawFrame(35, 111, 29, 35);
  ucg.drawBox(70, 112, 3, 7);
  ucg.drawBox(70, 136, 3, 7);
  ucg.drawLine(69, 106, 95, 100);
  ucg.drawLine(95, 100, 95, 144);
  ucg.drawLine(95, 144, 69, 150);
  ucg.drawBox(90, 119, 3, 10);
}

void renderDisplay(float temperature, float internalTemperature, bool co2Valid) {
  bool co2AtTarget = co2Valid && CO2i >= CO2_CONTROL_MIN_PPM && CO2i <= CO2_CONTROL_MAX_PPM;
  bool temperatureAtTarget = !isnan(temperature) &&
                             temperature >= TEMPERATURE_GOOD_MIN && temperature <= TEMPERATURE_GOOD_MAX;
  uint8_t conditionsAtTarget = (co2AtTarget ? 1 : 0) + (temperatureAtTarget ? 1 : 0);
  int8_t healthState = conditionsAtTarget == 0 ? DISPLAY_FAULT :
                       (conditionsAtTarget == 1 ? DISPLAY_WAIT : DISPLAY_READY);
  uint8_t safetyAlert = safetyFault ? safetyFault : (isnan(temperature) ? 3 : 0);
  int8_t rangeLockState = co2RangeWrapLatched ? 1 : 0;
  bool lockChanged = rangeLockState != displayCo2RangeLock;
  if (healthState != displayHealthState || lockChanged || safetyAlert != displaySafetyAlert) {
    displayHealthState = healthState;
    displayCo2RangeLock = rangeLockState;
    displaySafetyAlert = safetyAlert;
    if (lockChanged) displayCo2RateReady = -1;
    drawHealthIndicator();
  }
  int16_t tempTenths = isnan(temperature) ? -32768 : (int16_t)(temperature * 10.0f + (temperature >= 0 ? 0.5f : -0.5f));
  int16_t internalTempTenths = isnan(internalTemperature) ? -32768 : (int16_t)(internalTemperature * 10.0f + (internalTemperature >= 0 ? 0.5f : -0.5f));
  int8_t co2Quality = !co2Valid ? 0 : (co2AtTarget ? 1 :
    (CO2i >= CO2_TARGET_PPM - CO2_DISPLAY_NEAR_TOLERANCE_PPM &&
     CO2i <= CO2_TARGET_PPM + CO2_DISPLAY_NEAR_TOLERANCE_PPM ? 2 : -1));
  int8_t tempQuality = isnan(temperature) ? 0 : (temperatureAtTarget ? 1 :
    (temperature >= TEMPERATURE_DISPLAY_NEAR_MIN &&
     temperature <= TEMPERATURE_DISPLAY_NEAR_MAX ? 2 : -1));

  bool alert = co2Quality <= 0 || tempQuality <= 0 || safetyAlert || co2RangeWrapLatched;
  if (alert != displayAlert || displayDoorMode != co2DoorMode) {
    displayAlert = alert;
    displayDoorMode = co2DoorMode;
    drawDisplayFrame();
  }

  if (!displayCacheValid || displayCo2Ppm != CO2i || displayCo2Quality != co2Quality) {
    // Mantém os ppm grandes com a fonte numérica compacta do Uno.
    ucg.setFont(incubadora_font_inr16);
    char nextCo2Text[8];
    if (CO2i >= 0) ltoa(CO2i, nextCo2Text, 10);
    else strcpy_P(nextCo2Text, PSTR("---"));
    uint8_t co2R = co2Quality == 1 ? 70 : 255;
    uint8_t co2G = co2Quality == 1 ? 235 : (co2Quality == 2 ? 190 : 65);
    uint8_t co2B = co2Quality == 1 ? 145 : (co2Quality == 2 ? 45 : 75);
    drawTextChanges(nextCo2Text, 5, 40, 23, 18, 120,
                    co2R, co2G, co2B);
    displayCo2Ppm = CO2i;
    displayCo2Quality = co2Quality;
  }

  ucg.setFont(incubadora_font_7x13);
  if (!displayCacheValid || displayTempTenths != tempTenths || displayTempQuality != tempQuality) {
    char nextTempText[8];
    formatTenths(tempTenths, nextTempText);
    uint8_t tempR = tempQuality == 1 ? 70 : 255;
    uint8_t tempG = tempQuality == 1 ? 235 : (tempQuality == 2 ? 190 : 65);
    uint8_t tempB = tempQuality == 1 ? 145 : (tempQuality == 2 ? 45 : 75);
    drawTextChanges(nextTempText, 5, 74, 64, 12, 58,
                    tempR, tempG, tempB);
    // Bold overprint keeps the compact font and its fixed field width on the Uno.
    ucg.setPrintPos(6, 74);
    ucg.print(nextTempText);
    displayTempTenths = tempTenths;
    displayTempQuality = tempQuality;
  }
  if (!displayCacheValid || displayInternalTempTenths != internalTempTenths) {
    char nextInternalTempText[8];
    formatTenths(internalTempTenths, nextInternalTempText);
    drawTextChanges(nextInternalTempText, 66, 74, 64, 12, 59,
                    230, 235, 240);
    displayInternalTempTenths = internalTempTenths;
  }
  if (co2DoorMode == 2) {
    if (!displayCacheValid) drawDoorNotice();
    displayCacheValid = true;
    return;
  }

  bool co2RateValid = co2RatePpmMinReady;
  int32_t shownCo2Rate = co2RateValid ? co2RatePpmMin : 0;
  if (!displayCacheValid || displayCo2RatePpmMin != shownCo2Rate || displayCo2RateReady != co2RateValid) {
    char nextRateText[8];
    formatPpmPerMinute(shownCo2Rate, co2RateValid, nextRateText);
    ucg.setFont(incubadora_font_7x13);
    uint8_t rateR = !co2RateValid ? 145 : (shownCo2Rate < 0 ? 255 : (shownCo2Rate > 0 ? 120 : 75));
    uint8_t rateG = !co2RateValid ? 155 : (shownCo2Rate < 0 ? 115 : (shownCo2Rate > 0 ? 215 : 220));
    uint8_t rateB = !co2RateValid ? 165 : (shownCo2Rate < 0 ? 75 : (shownCo2Rate > 0 ? 250 : 145));
    drawTextChanges(nextRateText, 73, 101, 91, 13, 54,
                    rateR, rateG, rateB);
    displayCo2RatePpmMin = shownCo2Rate;
    displayCo2RateReady = co2RateValid;
  }

  bool shownLossStable = lossStable;
  bool lossHeld = lossCm3HourX10 >= 0 && !lossFresh;
  if (!displayCacheValid || displayLossCm3Hour != lossCm3HourX10 ||
      displayLossStable != shownLossStable || displayLossHeld != lossHeld) {
    char nextLossText[14];
    if (lossCm3HourX10 >= 0) {
      formatTenths(lossCm3HourX10, nextLossText);
      nextLossText[strlen(nextLossText) - 2] = '\0';
    }
    else strcpy_P(nextLossText, PSTR("---"));
    if (lossHeld) strcat_P(nextLossText, PSTR("*"));
    ucg.setFont(incubadora_font_7x13);
    drawTextChanges(nextLossText, 73, 120, 110, 12, 54,
                    shownLossStable ? 230 : 255,
                    shownLossStable ? 235 : 190, shownLossStable ? 240 : 45);
    displayLossCm3Hour = lossCm3HourX10;
    displayLossStable = shownLossStable;
    displayLossHeld = lossHeld;
  }

  if (!displayCacheValid || displayCo2Enabled != botao_co2_onoff) {
    bool co2Flowing = digitalRead(CO2PUMP) == LOW;
    drawCo2Icon(11, 137, botao_co2_onoff, co2Flowing, activityIconFrame & 3);
    displayCo2Active = co2Flowing;
    displayCo2Enabled = botao_co2_onoff;
  }
  if (!displayCacheValid || displayHeaterEnabled != botao_aquecedor_onoff) {
    bool heating = digitalRead(HEATER) == LOW;
    drawHeaterIcon(53, 136, botao_aquecedor_onoff, heating, activityIconFrame & 3);
    displayHeaterActive = heating;
    displayHeaterEnabled = botao_aquecedor_onoff;
  }
  if (!displayCacheValid || displayFanOn != ventilador_status) {
    drawFanIcon(98, 137, ventilador_status, ventilador_status != 0, activityIconFrame % 12);
    displayFanOn = ventilador_status;
  }
  displayCacheValid = true;
  updateActivityIcons();
}

void printStatus(unsigned long now) {
  Serial.print(F("STATUS,ms=")); Serial.print(now);
  Serial.print(F(",co2_ppm=")); Serial.print(CO2i);
  Serial.print(F(",co2_valid=")); Serial.print(CO2i > 0 && CO2i <= CO2_SENSOR_PROTOCOL_MAX_PPM && !co2RangeWrapLatched ? 1 : 0);
  Serial.print(F(",co2_range_lock=")); Serial.print(co2RangeWrapLatched ? 1 : 0);
  Serial.print(F(",boot_count=")); Serial.print(eeprom_contador_int);
  Serial.print(F(",temp_c=")); printFixed(chamberTemperatureC, 2);
  Serial.print(F(",humidity_pct=")); printFixed(NAN, 1);
  Serial.print(F(",internal_temp_c=")); printFixed(dhtint.readTemperature(), 1);
  Serial.print(F(",co2_enabled=")); Serial.print(botao_co2_onoff);
  Serial.print(F(",heater_enabled=")); Serial.print(botao_aquecedor_onoff);
  Serial.print(F(",fan_on=")); Serial.print(ventilador_status);
  Serial.print(F(",valve_open=")); Serial.print(digitalRead(CO2PUMP) == LOW ? 1 : 0);
  Serial.print(F(",heater_on=")); Serial.print(digitalRead(HEATER) == LOW ? 1 : 0);
  Serial.print(F(",pump_wait_cycles=")); Serial.print(contador_pomp);
  Serial.print(F(",loss_x10=")); Serial.print(lossCm3HourX10);
  Serial.print(F(",loss_ok=")); Serial.print(displayLossStable == 1 ? 1 : 0);
  Serial.println();
}

bool manualCo2Pulse(const char *source, uint16_t pulseMs = MANUAL_CO2_PULSE_MS) {
  if (co2DoorMode == 2) {
    Serial.println(F("ERR,DOOR_OPEN"));
    return false;
  }
  unsigned long now = millis();
  bool freshReading = lastCo2ReadingValid && now - lastValidCo2Time <= 5000UL;
  if ((CO2i > 0 && CO2i >= CO2_CONTROL_MAX_PPM) || digitalRead(CO2PUMP) == LOW) {
    Serial.println(F("ERR,CO2_PRIME_LIMIT_OR_VALVE_BUSY"));
    return false;
  }
  if (co2RangeWrapLatched) {
    Serial.println(F("ERR,CO2_RANGE_LOCKED"));
    return false;
  }
  co2BaselineReady = freshReading && CO2i > 0;
  if (co2BaselineReady) co2_before_pump = CO2i;
  max_co2_increase = 0;
  co2StableSince = 0;
  co2TrendReady = false;
  co2ReferenceReady = freshReading;
  if (freshReading) last_co2i = CO2i;
  if (pulseMs < MANUAL_CO2_PULSE_MS) pulseMs = MANUAL_CO2_PULSE_MS;
  if (pulseMs > MANUAL_CO2_MAX_PULSE_MS) pulseMs = MANUAL_CO2_MAX_PULSE_MS;
  lastCo2PulseMs = pulseMs;
  co2LastPulseAt = now;
  co2MaxRiseAt = now;

  co2DoseResponsePending = co2BaselineReady;
  maxRate = 0;
  if (!freshReading) lossFresh = false;
  finishCo2Loss();
  if (co2DoorMode == 4) co2DoorMode = 3;
  digitalWrite(CO2PUMP, LOW);
  delay(pulseMs);
  digitalWrite(CO2PUMP, HIGH);
  co2AnimationUntil = millis() + 3000UL;
  contador_pomp = POMP_WAITING_TIME;
  Serial.print(F("EVENT,co2_manual_pulse,")); Serial.print(source); Serial.print(','); Serial.print(pulseMs);
  Serial.print(F("ms,baseline,")); if (co2BaselineReady) Serial.println(F("valid")); else Serial.println(F("pending"));
  return true;
}

void handleSerialCommand() {
  if (strcmp_P(serialCommandBuffer, PSTR("STATUS")) == 0) {
    printStatus(millis());
  } else if (strcmp_P(serialCommandBuffer, PSTR("HELP")) == 0) {
    Serial.println(F("CMD: STATUS, CO2 ON/OFF/PRIME/LOCK/ACK, HEAT ON/OFF, ALL OFF"));
  } else if (strcmp_P(serialCommandBuffer, PSTR("CO2 ON")) == 0) {
    co2ClickCount = 0;
    if (setCo2Enabled(true)) Serial.println(F("ACK,CO2,ON"));
    else Serial.println(co2DoorMode == 2 ? F("ERR,DOOR_OPEN") :
                        F("ERR,CO2_RANGE_LOCKED; send CO2 ACK after external verification"));
  } else if (strcmp_P(serialCommandBuffer, PSTR("CO2 ACK")) == 0) {
    clearCo2RangeLock();
  } else if (strcmp_P(serialCommandBuffer, PSTR("CO2 LOCK")) == 0) {
    setCo2Enabled(false);
    co2RangeWrapLatched = true;
    mySensorCO2.rawLoggingEnabled = true;
    EEPROM.update(EEPROM_CO2_RANGE_LOCK, CO2_SENSOR_LOCK_MAGIC);
    Serial.println(F("ACK,CO2,RANGE_LOCKED_AUTO_OFF"));
  } else if (strcmp_P(serialCommandBuffer, PSTR("CO2 OFF")) == 0 || strcmp_P(serialCommandBuffer, PSTR("ALL OFF")) == 0) {
    co2ClickCount = 0; setCo2Enabled(false);
    if (strcmp_P(serialCommandBuffer, PSTR("ALL OFF")) == 0) {
      setHeaterEnabled(false);
      Serial.println(F("ACK,ALL,OFF"));
    } else Serial.println(F("ACK,CO2,OFF"));
  } else if (strcmp_P(serialCommandBuffer, PSTR("CO2 PRIME")) == 0) {
    if (manualCo2Pulse("serial")) Serial.println(F("ACK,CO2,PRIME"));
  } else if (strcmp_P(serialCommandBuffer, PSTR("HEAT ON")) == 0) {
    setHeaterEnabled(true);
    Serial.println(botao_aquecedor_onoff ? F("ACK,HEAT,ON") : F("ERR,DOOR_OPEN"));
  } else if (strcmp_P(serialCommandBuffer, PSTR("HEAT OFF")) == 0) {
    setHeaterEnabled(false);
    Serial.println(F("ACK,HEAT,OFF"));
  } else if (serialCommandLength > 0) {
    Serial.println(F("ERR,UNKNOWN_COMMAND; send HELP"));
  }
}

void saveControlState() {
  EEPROM.update(EEPROM_CONTROL_STATE, botao_co2_onoff | (botao_aquecedor_onoff << 1) |
    (co2DoorMode == 2 ? 4 | (doorResumeControls << 3) : 0));
}

bool setCo2Enabled(bool enabled) {
  if (enabled && (co2RangeWrapLatched || co2DoorMode == 2)) return false;
  if (enabled && safetyFault) {
    safetyFault = 0;
    EEPROM.update(EEPROM_SAFETY_FAULT, 0);
  }
  if (!enabled && co2DoorMode >= 3) co2DoorMode = 0;
  botao_co2_onoff = enabled;
  saveControlState();
  if (!enabled) digitalWrite(CO2PUMP, HIGH);
  return true;
}

void setHeaterEnabled(bool enabled) {
  if (enabled && co2DoorMode == 2) return;
  if (enabled && safetyFault) {
    safetyFault = 0;
    EEPROM.update(EEPROM_SAFETY_FAULT, 0);
  }
  botao_aquecedor_onoff = enabled;
  saveControlState();
  if (!enabled && digitalRead(HEATER) == LOW) {
    digitalWrite(HEATER, HIGH);
    heaterLastTransitionAt = millis();
    heaterPidDemandMs = 0;
  }
  if (!enabled) heaterPidIntegralMs = 0.0f;
}

void controlHeater(float temperature, unsigned long now) {
  bool heaterOn = digitalRead(HEATER) == LOW;
  bool emergencyOvertemperature = temperature >= HEATER_EMERGENCY_CUTOFF;
  bool temperatureSensorFault = isnan(temperature);
  if (emergencyOvertemperature &&
      (botao_aquecedor_onoff != 0 || botao_co2_onoff != 0 || heaterOn)) {
    safetyFault = 2;
    EEPROM.update(EEPROM_SAFETY_FAULT, 0xC2);
    Serial.println(F("EVT,SAFE_OFF"));
    setHeaterEnabled(false);
    setCo2Enabled(false);
    heaterOn = false;
  } else if (temperatureSensorFault) {
    if (heaterSensorFaultSince == 0) heaterSensorFaultSince = now;
    if (heaterSensorFaultSince != 0 &&
        now - heaterSensorFaultSince >= 60000UL &&
        (botao_aquecedor_onoff != 0 || botao_co2_onoff != 0)) {
      safetyFault = 1;
      EEPROM.update(EEPROM_SAFETY_FAULT, 0xC1);
      Serial.println(F("EVT,SAFE_OFF"));
      setHeaterEnabled(false);
      setCo2Enabled(false);
    } else if (heaterOn) {
      digitalWrite(HEATER, HIGH);
      heaterLastTransitionAt = now;
    }
  } else {
    heaterSensorFaultSince = 0;
  }
  if (botao_aquecedor_onoff != 1 || temperatureSensorFault || emergencyOvertemperature) {
    if (heaterOn) {
      digitalWrite(HEATER, HIGH);
      heaterLastTransitionAt = now;
    }
    heaterPidDemandMs = 0;
    heaterPidIntegralMs = 0.0f;
    heaterPidInitialized = false;
    heaterTrendReady = false;
    return;
  }

  if (!heaterPidInitialized) {
    heaterPidInitialized = true;
    heaterPidLastUpdateAt = now;
    heaterTrendReferenceAt = now;
    heaterTrendReferenceC = temperature;
    heaterTempRateCPerMin = 0.0f;
    heaterPidIntegralMs = 0.0f;
    heaterTrendReady = false;
  }

  unsigned long elapsedMs = now - heaterPidLastUpdateAt;
  if (now - heaterTrendReferenceAt >= HEATER_TREND_WINDOW_MS) {
    unsigned long trendElapsedMs = now - heaterTrendReferenceAt;
    float measuredRate = (temperature - heaterTrendReferenceC) * 60000.0f /
                         (float)trendElapsedMs;
    // Smooth the 30-second sensor trend so one quantization step does not
    // make the relay chase measurement noise.
    heaterTempRateCPerMin = heaterTrendReady
      ? heaterTempRateCPerMin * 0.5f + measuredRate * 0.5f
      : measuredRate;
    heaterTrendReferenceAt = now;
    heaterTrendReferenceC = temperature;
    heaterTrendReady = true;
  }

  float errorC = HEATER_SETPOINT_C - temperature;
  if (errorC < 0.0f || heaterPidDemandMs < HEATER_PID_MAX_ON_MS) {
    heaterPidIntegralMs += errorC * HEATER_PID_KI_MS_PER_C_MIN *
                           ((float)elapsedMs / 60000.0f);
    if (heaterPidIntegralMs < 0.0f) heaterPidIntegralMs = 0.0f;
    if (heaterPidIntegralMs > HEATER_PID_MAX_ON_MS) {
      heaterPidIntegralMs = HEATER_PID_MAX_ON_MS;
    }
  }
  // At the exact setpoint, retain the PI/D trim so the heater can balance
  // steady heat loss instead of cycling only after a full 0.1 C drop.
  if (errorC < 0.0f || temperature >= HEATER_HARD_CUTOFF) {
    heaterPidDemandMs = 0;
  } else {
    float derivativeMs = heaterTrendReady
      ? -HEATER_PID_KD_MS_PER_C_MIN * heaterTempRateCPerMin
      : 0.0f;
    float demandMs = HEATER_PID_KP_MS_PER_C * errorC +
                     heaterPidIntegralMs + derivativeMs;
    if (demandMs < 0.0f) demandMs = 0.0f;
    if (demandMs > HEATER_PID_MAX_ON_MS) demandMs = HEATER_PID_MAX_ON_MS;
    heaterPidDemandMs = (uint16_t)(demandMs + 0.5f);
  }
  heaterPidLastUpdateAt = now;
  if (heaterOn && heaterPidDemandMs < heaterCurrentPulseMs) {
    heaterCurrentPulseMs = heaterPidDemandMs;
  }

  // Allow controlled heating through the narrow
  // deadband so a quantized cutoff reading does not force a long coast downward.
  bool safeToHeat = temperature <= HEATER_HARD_CUTOFF &&
                    temperature < HEATER_HARD_CUTOFF;
  if (heaterOn && (!safeToHeat || now - heaterPulseStartedAt >= heaterCurrentPulseMs)) {
    digitalWrite(HEATER, HIGH);
    heaterLastTransitionAt = now;
  } else if (!heaterOn && safeToHeat && heaterPidDemandMs > 0 &&
             now - heaterLastTransitionAt >= HEATER_MIN_OFF_MS) {
    heaterCurrentPulseMs = heaterPidDemandMs;
    heaterPulseStartedAt = now;
    digitalWrite(HEATER, LOW);
    heaterLastTransitionAt = now;
  }
}

void finishCo2ClickSequence() {
  if (co2ClickCount == 0) return;
  uint8_t clicks = co2ClickCount;
  co2ClickCount = 0;
  Serial.print(F("EVENT,co2_button_clicks,")); Serial.println(clicks);
  if (clicks >= 3) {
    uint16_t pulseMs = clicks == 3 ? MANUAL_CO2_PULSE_MS :
                       (clicks == 4 ? 10 : MANUAL_CO2_MAX_PULSE_MS);
    manualCo2Pulse(clicks == 3 ? "button_3" : (clicks == 4 ? "button_4" : "button_5"), pulseMs);
    return;
  }
  bool targetState = co2ModeAtClickSequence ^ (clicks & 1);
  setCo2Enabled(targetState);
}

void clearCo2RangeLock() {
  setCo2Enabled(false);
  EEPROM.update(EEPROM_CO2_RANGE_LOCK, 0);
  co2RangeWrapLatched = false;
  mySensorCO2.rawLoggingEnabled = false;
  co2RawReferenceReady = false;
  co2ReferenceReady = false;
  Serial.println(F("ACK,CO2,RANGE_UNLOCKED_AUTO_OFF"));
}

void finishHeaterClickSequence() {
  uint8_t clicks = heaterClickCount;
  heaterClickCount = 0;
  if (clicks >= 3 && co2RangeWrapLatched) {
    clearCo2RangeLock();
    Serial.println(F("EVENT,co2_lock_cleared,heater_three_clicks"));
  } else if (clicks & 1) setHeaterEnabled(!botao_aquecedor_onoff);
}

void handleHeaterButtonClick(unsigned long now) {
  if (heaterClickCount == 0) heaterClickSequenceStart = now;
  if (heaterClickCount < 3) heaterClickCount++;
  if (heaterClickCount == 3 && co2RangeWrapLatched) finishHeaterClickSequence();
}

void handleCo2ButtonClick(unsigned long now) {
  if (co2ClickCount == 0) {
    co2ClickSequenceStart = now;
    co2ModeAtClickSequence = botao_co2_onoff;
  }
  co2ClickCount++;
  if (co2ClickCount >= 5) {
    Serial.println(F("EVENT,co2_button_clicks,5"));
    co2ClickCount = 0;
    manualCo2Pulse("button_5", MANUAL_CO2_MAX_PULSE_MS);
  }
}

void toggleDoorMode() {
  co2ClickCount = heaterClickCount = 0;
  co2DoseResponsePending = false;
  finishCo2Loss();
  if (co2DoorMode == 2) {
    co2DoorMode = 4;
    if (!safetyFault) {
      setHeaterEnabled(doorResumeControls & 2);
      setCo2Enabled(doorResumeControls & 1);
    }
    if (!botao_co2_onoff) co2DoorMode = 0;
  } else {
    doorResumeControls = botao_co2_onoff | (botao_aquecedor_onoff << 1);
    co2DoorMode = 2;
    setCo2Enabled(false);
    setHeaterEnabled(false);
  }
  saveControlState();
  displayCacheValid = false;
  Serial.print(F("EVENT,door,"));
  Serial.println(co2DoorMode == 2 ? F("open") : F("closed"));
}

void dispatchHeaterClick(unsigned long now) {
  if (co2RangeWrapLatched) handleHeaterButtonClick(now);
  else setHeaterEnabled(!botao_aquecedor_onoff);
}

void serviceHeaterButton(bool pressedEdge, bool bothPressed, unsigned long now) {
  if (bothPressed) {
    heaterPressPending = false;
    return;
  }
  if (pressedEdge) {
    heaterPressPending = true;
    heaterPressedAt = now;
  }
  if (!heaterPressPending) return;
  if (now - heaterPressedAt >= 2000UL) {
    heaterPressPending = false;
    toggleDoorMode();
  } else if (!heaterButtonStable) {
    heaterPressPending = false;
    dispatchHeaterClick(now);
  }
}

bool updateButtonState(int pin, bool &stable, bool &candidate, uint8_t &samples) {
  bool raw = analogRead(pin) > 500;
  if (raw == candidate) {
    if (samples < 3) samples++;
  } else {
    candidate = raw;
    samples = 1;
  }
  if (samples >= 3 && stable != candidate) {
    stable = candidate;
    return stable;
  }
  return false;
}

void serviceInputsForTwoSeconds() {
  unsigned long started = millis();
  while (millis() - started < 2000UL) {
    unsigned long now = millis();
    serviceChamberTemperature();
    controlHeater(chamberTemperatureC, now);
    processSerialCommands();
    finishCo2ClickSequenceIfExpired(now);
    bool co2Pressed = updateButtonState(BOTAO_CO2, co2ButtonStable, co2ButtonCandidate, co2ButtonDebounceCount);
    bool heaterPressed = updateButtonState(BOTAO_AQUECEDOR, heaterButtonStable, heaterButtonCandidate, heaterButtonDebounceCount);
    serviceActivityIconAnimation();
    bool bothPressed = co2ButtonStable && heaterButtonStable;
    if (bothPressed && !bothButtonsStable) {
      Serial.println(F("EVENT,both_buttons_pressed"));
      heaterPressPending = false;
      if (co2ClickCount > 0) setCo2Enabled(co2ModeAtClickSequence);
      co2ClickCount = 0;
      eeprom_contador_int = 0;
      EEPROM.put(EEPROM_CONTADOR, eeprom_contador_int);
      drawHealthIndicator();
    } else if (!bothPressed) {
      if (co2Pressed) handleCo2ButtonClick(now);
    }
    serviceHeaterButton(heaterPressed, bothPressed, now);
    bothButtonsStable = bothPressed;
    delay(20);
  }
}

void finishCo2ClickSequenceIfExpired(unsigned long now) {
  if (co2ClickCount > 0 && now - co2ClickSequenceStart >= 3000UL) finishCo2ClickSequence();
  if (heaterClickCount > 0 && now - heaterClickSequenceStart >= 1500UL) finishHeaterClickSequence();
}

void processSerialCommands() {
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\r' || c == '\n') {
      if (serialCommandLength > 0) {
        serialCommandBuffer[serialCommandLength] = '\0';
        handleSerialCommand();
        serialCommandLength = 0;
      }
    } else if (serialCommandLength < sizeof(serialCommandBuffer) - 1) {
      if (c >= 'a' && c <= 'z') c -= ('a' - 'A');
      serialCommandBuffer[serialCommandLength++] = c;
    } else {
      serialCommandLength = 0;
      Serial.println(F("ERR,COMMAND_TOO_LONG"));
    }
  }
}

void disableAutoCalibration() {
  // Command to disable auto-calibration
  // byte disableAutoCalib[] = {0xFF, 0x01, 0x79, 0xA0, 0x00, 0x00, 0x00, 0x00, 0x86}; // Adjust checksum as needed
  byte disableAutoCalib[] = {0xFF, 0x01, 0x79, 0x00, 0x00, 0x00, 0x00, 0x00, 0x86}; // Adjust checksum as needed
  mySerialCO2.write(disableAutoCalib, 9);

  // Drain the sensor's acknowledgement without sending diagnostic text to USB serial.
  delay(500);
  while (mySerialCO2.available()) {
    mySerialCO2.read();
  }
}


// Função para calcular o tempo de abertura
int32_t calcularDelayProporcional(int32_t ppm_atual, int32_t ppm_objetivo, int32_t ganhoPpmPorMsX100, bool tendenciaValida, int32_t pulseLimit) {
  if (!tendenciaValida || ppm_atual <= 0 || ppm_objetivo <= ppm_atual ||
      ganhoPpmPorMsX100 <= 0) {
    return DELAY_MINIMO;
  }
  int32_t ppmNecessario = ppm_objetivo - ppm_atual;
  // Suaviza em 1/3 a eficiência medida a cada resposta estabilizada, acompanhando
  // a pressão variável sem deixar uma única amostra definir todo o pulso seguinte.
  // O sensor pode refletir a injeção muitos segundos depois de fechar a válvula.
  // Reduce the fraction as projected leakage grows, keeping the steady error
  // caused by delayed feedback within the configured CO2 tolerance.
  int32_t lossRate = co2RatePpmMin;
  if (lossRate > 0) lossRate = 0;
  if (lossRate < -5000) lossRate = -5000;
  int32_t lossPerResponse = -lossRate * co2ResponseLagSeconds / 60L;
  uint8_t fractionDenominator = co2DoorMode >= 3 ? 1 :
    (ppmNecessario > CO2_TOLERANCE_PPM ? 2 : 3);
  if (co2DoorMode < 3 && lossPerResponse > CO2_TOLERANCE_PPM / 2) {
    fractionDenominator = 1 + CO2_TOLERANCE_PPM / lossPerResponse;
  }
  int32_t tempoValvula = ppmNecessario * 100L /
                         (ganhoPpmPorMsX100 * fractionDenominator);
  if (tempoValvula < DELAY_MINIMO) return DELAY_MINIMO;
  if (tempoValvula > pulseLimit) return pulseLimit;
  return (int32_t)tempoValvula;
}


//void wakeUpScreen() {
//    ucg.sendCommand(0x11); // Sleep Out command
//    delay(120);            // Wait for the screen to wake up
//    ucg.sendCommand(0x29); // Display ON
//    Serial.println("Screen awakened");
//}

// funciona
//void reinitializeScreen() {
//    ucg.begin(UCG_FONT_MODE_TRANSPARENT);
//    ucg.setRotate90();
//    ucg.setFont(ucg_font_inr16_mr);
//    Serial.println("Screen reinitialized");
//}

// funciona 2
// ucg.begin(UCG_FONT_MODE_TRANSPARENT);
// ucg.setRotate180();
// ucg.setFont(ucg_font_inr16_mr);
// ucg.setRotate180();

//funciona 3
//ucg.begin(UCG_FONT_MODE_TRANSPARENT);
//ucg.setRotate180();
//ucg.setRotate180();
