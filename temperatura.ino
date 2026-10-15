#include <Arduino.h>
#include <SoftwareSerial.h>     
#include <SPI.h>
#include "Ucglib.h"
#include <NDIRZ16.h>
#include <avr/wdt.h>
#include <EEPROM.h>
#include <avr/pgmspace.h>
#include <string.h>

#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

//#define ERROR_LOG_ADDRESS 0 // EEPROM address to store error log
#define EEPROM_CONTADOR 24
#define EEPROM_CO2_RANGE_LOCK 28

#define DHTPIN 4
#define DHT_TEMPERATURA_INT_PIN 2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);
DHT dhtint(DHT_TEMPERATURA_INT_PIN, DHTTYPE);

#define HEATER 6
#define CO2PUMP 7
#define BOTAO_CO2 1
#define BOTAO_AQUECEDOR 0
#define BAUDRATE 9600                                      // Device to MH-Z19 Serial baudrate (should not be changed)

#define CO2_TARGET_PPM 50000L
#define CO2_TOLERANCE_PPM 1000L
#define CO2_CONTROL_MIN_PPM (CO2_TARGET_PPM - CO2_TOLERANCE_PPM)
#define CO2_CONTROL_MAX_PPM (CO2_TARGET_PPM + CO2_TOLERANCE_PPM)
#define CO2_SENSOR_PROTOCOL_MAX_PPM 65535L
#define CO2_SENSOR_LOCK_PPM 60000L
#define CO2_SENSOR_LOCK_MAGIC 0xA5
#define CO2_SENSOR_WARMUP_MS 180000UL
#define CO2_GOOD_MIN_PPM CO2_CONTROL_MIN_PPM
#define CO2_MAX_RISING_RATE_PPM_PER_MIN 300L
#define CO2_STABLE_TIME_MS 30000UL
#define CO2_RESPONSE_LAG_DEFAULT_MS 60000UL
#define CO2_RESPONSE_LAG_MIN_MS 30000UL
#define CO2_RESPONSE_LAG_MAX_MS 180000UL
#define HEATER_SETPOINT_C 37.0
#define HEATER_MIN_OFF_MS 10000UL
#define HEATER_PID_MAX_ON_MS 20000UL
#define HEATER_TREND_WINDOW_MS 30000UL
#define HEATER_PID_KP_MS_PER_C 32000.0f
#define HEATER_PID_KI_MS_PER_C_MIN 6000.0f
#define HEATER_PID_KD_MS_PER_C_MIN 6000.0f
#define HEATER_HARD_CUTOFF 37.1
#define HEATER_EMERGENCY_CUTOFF 38.0
#define TEMPERATURE_GOOD_MIN 36.9
#define TEMPERATURE_GOOD_MAX 37.1
#define POMP_WAITING_TIME 30 // Cerca de 1 minuto com o ciclo atual de 2 s para o MH-Z perceber o pulso
#define MAX_INTERNAL_TEMP 31 // Liga fan acima de 31 C; desliga abaixo de 30 C

#define VENTILADOR_PIN 3

SoftwareSerial mySerialCO2(12,5);
NDIRZ16 mySensorCO2 = NDIRZ16(&mySerialCO2);
Ucglib_ST7735_18x128x160_HWSPI ucg(/*cd=*/ 9, /*cs=*/ 10, /*reset=*/ 8);

int botao_co2_onoff = 0;
int botao_aquecedor_onoff = 0;
int32_t last_co2i = 0;
int contador_pomp;
int32_t CO2i = 0;
int32_t lastCo2RawPpm = 0;
uint16_t lastCo2PulseMs = 0;
int32_t eeprom_contador_int = 0;
int ventilador_status = 0;
unsigned long heaterPidLastUpdateAt = 0;
unsigned long heaterLastTransitionAt = 0;
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
int16_t displayTempTenths = 32767;
int16_t displayHumidityPercent = 32767;
int16_t displayInternalTempTenths = 32767;
char displayCo2Text[8] = "";
char displayTempText[8] = "";
char displayHumidityText[8] = "";
char displayInternalTempText[8] = "";
char displayCo2RateText[8] = "";
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
int co2ModeAtClickSequence = 0;
unsigned long co2ClickSequenceStart = 0;
bool bothButtonsStable = false;

// Variáveis para calcular a taxa de aumento de CO2
float co2Rate = 0; // Armazena a taxa de aumento do CO2
float maxRate = 0;
int32_t co2_before_pump = 0;
int32_t max_co2_increase = 0;
// Limites de taxa e delay para liberacao da valvula de CO2 proporcional a pressao
// analise: 1436ppm/s pra 0.5kg/cm2 com a valvula aperta por 5ms
const float TAXA_MAXIMA = 1000.0; // ppm/s
const float TAXA_MINIMA = 10.0;   // ppm/s
const int DELAY_MAXIMO = 250;    // ms; teto inicial, reduzido dinamicamente ao aproximar do alvo
const int DELAY_MINIMO = 5;       // ms; evita pulsos abaixo da resolução útil da válvula
const int CO2_BOOTSTRAP_PPM_PER_MS = 12; // Maior resposta observada nos ensaios: ~11,8 ppm/ms
const int32_t CO2_MIN_GAIN_ESTIMATE_X100 = 50; // Evita divisão por zero: 0,5 ppm/ms
const int CO2_DOSE_FRACTION_DENOMINATOR = 4; // Doses maiores, ainda fracionadas para respeitar a resposta atrasada
const int MANUAL_CO2_PULSE_MS = 5; // Pulso curto já citado como referência experimental
const int MANUAL_CO2_MAX_PULSE_MS = 20;
#define DISPLAY_FAULT 0
#define DISPLAY_WAIT 1
#define DISPLAY_READY 2
int8_t displayHealthState = DISPLAY_WAIT;
int32_t co2GainEstimatePpmPerMsX100 = CO2_BOOTSTRAP_PPM_PER_MS * 100L;
bool co2DoseResponsePending = false;
unsigned long co2LastPulseAt = 0;
unsigned long co2MaxRiseAt = 0;
uint8_t co2ResponseLagSeconds = 60;
int32_t co2ProjectedPpm = 0;
int32_t co2RateAtPulsePpmMin = 0;
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

// Variáveis globais para aprendizado adaptativo
// float media_eficiencia = 0.0;
// int contagem_aberturas = 0;

void setup()
{  
    Serial.begin(9600);                                     // Device to serial monitor feedback

    // -------------------- DEBUG --------------------------

    co2RangeWrapLatched = EEPROM.read(EEPROM_CO2_RANGE_LOCK) == CO2_SENSOR_LOCK_MAGIC;
    mySensorCO2.rawLoggingEnabled = co2RangeWrapLatched;
    Serial.print(F("PreCO2: "));
    Serial.print(botao_co2_onoff);
    Serial.print(F(" PreTemp: "));
    Serial.println(botao_aquecedor_onoff);

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
    dht.begin();
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
    Serial.println(F("CO2 auto wait 180s sensor warmup"));
//    if (MCUSR & (1 << WDRF)) {
//      Serial.println("Watchdog reset detected.");
//      EEPROM.put(ERROR_LOG_ADDRESS, "Watchdog reset detected."); // Optionally log to EEPROM
//    }
    playLoadingDots();
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
      int32_t rawCo2Jump = sensorPpm - lastCo2RawPpm;
      if (sensorPpm >= CO2_SENSOR_LOCK_PPM && !co2RangeWrapLatched) {
        co2RangeWrapLatched = true;
        mySensorCO2.rawLoggingEnabled = true;
        EEPROM.update(EEPROM_CO2_RANGE_LOCK, CO2_SENSOR_LOCK_MAGIC);
        setCo2Enabled(false);
        Serial.println(F("EVENT,co2_near_protocol_limit,auto_locked_persistently"));
      }
      if (co2RawReferenceReady && (rawCo2Jump >= 15000 || rawCo2Jump <= -15000)) {
        co2RangeWrapLatched = true;
        mySensorCO2.rawLoggingEnabled = true;
        EEPROM.update(EEPROM_CO2_RANGE_LOCK, CO2_SENSOR_LOCK_MAGIC);
        setCo2Enabled(false);
        Serial.print(F("EVENT,co2_protocol_jump_suspected,delta_ppm,"));
        Serial.print(rawCo2Jump);
        Serial.println(F(",control_locked_until_restart"));
      }
      lastCo2RawPpm = sensorPpm;
      co2RawReferenceReady = true;
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
    bool responseWaitComplete = currentTime - co2LastPulseAt >=
      (unsigned long)co2ResponseLagSeconds * 1000UL;
    bool doseResponseReady = validCo2 && responseWaitComplete &&
                             contador_pomp == 0 && co2TrendReady;
    co2ProjectedPpm = CO2i;
    if (validCo2 && co2RatePpmMinReady && co2RatePpmMin < 0) {
      int32_t boundedRate = co2RatePpmMin;
      if (boundedRate < -5000) boundedRate = -5000;
      int32_t projected = CO2i + boundedRate * co2ResponseLagSeconds / 60L;
      if (projected < 0) projected = 0;
      co2ProjectedPpm = projected;
    }
    int32_t pulseLimit = DELAY_MINIMO;
    int32_t co2Deficit = CO2_TARGET_PPM - co2ProjectedPpm;
    if (validCo2 && co2Deficit > 0) {
      // Scale the pulse cap with the remaining deficit. A >>5 ramp responds
      // faster during large deficits while still tapering to short pulses
      // close to target; the observed dose gain continues to adapt each cycle.
      pulseLimit += co2Deficit >> 5;
      if (pulseLimit > DELAY_MAXIMO) pulseLimit = DELAY_MAXIMO;
    }
    int32_t delayProporcional = validCo2
      ? calcularDelayProporcional(co2ProjectedPpm, CO2_TARGET_PPM, co2GainEstimatePpmPerMsX100, doseResponseReady, pulseLimit)
      : DELAY_MINIMO;

    
    float h = dht.readHumidity();
    float t = dht.readTemperature();
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

    if (validCo2 && currentTime >= CO2_SENSOR_WARMUP_MS &&
        co2ProjectedPpm < CO2_CONTROL_MIN_PPM && botao_co2_onoff == 1 &&
        doseResponseReady && co2ClickCount == 0) {
      co2_before_pump = CO2i;
      co2BaselineReady = true;
      int32_t pulseMs;
      if (lastCo2PulseMs == 0) {
        int32_t ppmNeeded = CO2_TARGET_PPM - co2ProjectedPpm;
        pulseMs = ppmNeeded / CO2_BOOTSTRAP_PPM_PER_MS;
        Serial.print(F("EVENT,co2_pulse,first,ms,"));
      } else {
        if (co2DoseResponsePending && lastCo2PulseMs > 0) {
          unsigned long responseWindowMs = co2MaxRiseAt > co2LastPulseAt
            ? co2MaxRiseAt - co2LastPulseAt : (unsigned long)co2ResponseLagSeconds * 1000UL;
          int32_t ambientChangePpm = co2RateAtPulsePpmMin *
            (int32_t)responseWindowMs / 60000L;
          int32_t doseRisePpm = max_co2_increase - ambientChangePpm;
          if (doseRisePpm < 0) doseRisePpm = 0;
          int32_t observedGainX100 = doseRisePpm * 100L / lastCo2PulseMs;
          co2GainEstimatePpmPerMsX100 =
            (co2GainEstimatePpmPerMsX100 * 2L + observedGainX100) / 3L;
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
        Serial.print(F("EVENT,co2_pulse,ms,"));
      }
      if (pulseMs > pulseLimit) pulseMs = pulseLimit;
      if (pulseMs < DELAY_MINIMO) pulseMs = DELAY_MINIMO;
      lastCo2PulseMs = pulseMs;
      Serial.println(pulseMs);
      digitalWrite(CO2PUMP, LOW);
      delay(pulseMs);
      digitalWrite(CO2PUMP, HIGH);
      co2AnimationUntil = millis() + 3000UL;
      co2DoseResponsePending = true;
      max_co2_increase = 0;
      co2LastPulseAt = millis();
      co2MaxRiseAt = co2LastPulseAt;
      co2RateAtPulsePpmMin = co2RatePpmMinReady ? co2RatePpmMin : 0;
      if (co2RateAtPulsePpmMin < -5000) co2RateAtPulsePpmMin = -5000;
      if (co2RateAtPulsePpmMin > 5000) co2RateAtPulsePpmMin = 5000;
      co2StableSince = 0;
      co2TrendReady = false;
      contador_pomp = POMP_WAITING_TIME;
      maxRate = 0;
    } else {
      digitalWrite(CO2PUMP, HIGH);
    }

    renderDisplay(t, h, t_interna, validCo2);
    if (!serialHeaderPrinted) {
    Serial.println(F("DATA,ms,co2_ppm,co2_valid,temp_c,humidity_pct,internal_temp_c,co2_enabled,heater_enabled,heater_on,fan_on,valve_open,next_pulse_ms,last_pulse_ms,rate_ppm_s,rate_ppm_min_valid,rate_ppm_min,max_rate_ppm_s,delta_ppm,max_co2_rise_since_pump_ppm,pump_wait_cycles,trend_ready,heater_pid_demand_ms,heater_temp_rate_c_min,co2_range_lock,co2_projected_ppm"));
      serialHeaderPrinted = true;
    }
    Serial.print(F("DATA,")); Serial.print(currentTime); Serial.print(','); Serial.print(CO2i); Serial.print(','); Serial.print(validCo2 ? 1 : 0);
    Serial.print(','); printFixed(t, 1); Serial.print(','); printFixed(h, 1); Serial.print(','); printFixed(t_interna, 1);
    Serial.print(','); Serial.print(botao_co2_onoff); Serial.print(','); Serial.print(botao_aquecedor_onoff); Serial.print(',');
    Serial.print(digitalRead(HEATER) == LOW ? 1 : 0); Serial.print(','); Serial.print(ventilador_status); Serial.print(',');
    Serial.print(digitalRead(CO2PUMP) == LOW ? 1 : 0); Serial.print(','); Serial.print(delayProporcional); Serial.print(',');
    Serial.print(lastCo2PulseMs); Serial.print(',');
    printFixed(co2Rate, 2); Serial.print(','); Serial.print(co2RatePpmMinReady ? 1 : 0); Serial.print(','); Serial.print(co2RatePpmMin); Serial.print(',');
    printFixed(maxRate, 2); Serial.print(','); Serial.print(co2Delta); Serial.print(',');
    Serial.print(max_co2_increase); Serial.print(','); Serial.print(contador_pomp); Serial.print(','); Serial.print(co2TrendReady && contador_pomp == 0 ? 1 : 0); Serial.print(','); Serial.print(heaterPidDemandMs); Serial.print(','); printFixed(heaterTempRateCPerMin, 2); Serial.print(','); Serial.print(co2RangeWrapLatched ? 1 : 0); Serial.print(','); Serial.println(co2ProjectedPpm);

    if (contador_pomp > 0) contador_pomp--;
    serviceInputsForTwoSeconds(t);
    // delay(60000);
}



void reinitializeScreen() {
    ucg.begin(UCG_FONT_MODE_TRANSPARENT);
    ucg.setRotate180();
    drawDisplayFrame();
}

void drawCo2Icon(uint8_t x, uint8_t y, bool enabled, bool flowing, uint8_t frame) {
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(x - 2, y - 1, 25, 17);
  ucg.setColor(0, enabled ? 180 : 105, enabled ? 225 : 130, enabled ? 255 : 150);
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

void playLoadingDots() {
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(0, 0, ucg.getWidth(), ucg.getHeight());
  for (uint8_t frame = 0; frame < 60; frame++) {
    drawCo2Icon(52, 72, true, true, frame & 3);
    delay(160);
  }
  delay(400);
}

void drawHeaterIcon(uint8_t x, uint8_t y, bool enabled, bool heating, uint8_t frame) {
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(x - 1, y - 1, 23, 17);
  uint8_t red = enabled ? 255 : 135;
  uint8_t green = enabled ? 145 : 120;
  uint8_t blue = enabled ? 55 : 135;
  if (heating && (frame & 1)) green = 185;
  ucg.setColor(0, red, green, blue);
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
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(x - 1, y - 1, 21, 17);
  ucg.setColor(0, enabled ? 75 : 130, enabled ? 195 : 145, enabled ? 255 : 160);
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
  if (!displayCacheValid) return;
  unsigned long now = millis();
  bool co2Flowing = digitalRead(CO2PUMP) == LOW ||
                    (co2AnimationUntil != 0 && (int32_t)(now - co2AnimationUntil) < 0);
  bool heating = digitalRead(HEATER) == LOW;
  bool fanSpinning = ventilador_status != 0;
  uint8_t co2Frame = activityIconFrame & 3;
  uint8_t heaterFrame = activityIconFrame & 3;
  uint8_t fanFrame = activityIconFrame % 12;
  if (co2Flowing || displayCo2Active != co2Flowing) {
    drawCo2Icon(11, 120, botao_co2_onoff, co2Flowing, co2Frame);
    displayCo2Active = co2Flowing;
  }
  if (heating || displayHeaterActive != heating) {
    drawHeaterIcon(53, 121, botao_aquecedor_onoff, heating, heaterFrame);
    displayHeaterActive = heating;
  }
  if (fanSpinning || displayFanOn != fanSpinning) {
    drawFanIcon(98, 120, fanSpinning, fanSpinning, fanFrame);
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
  if (co2RangeWrapLatched || displayHealthState == DISPLAY_FAULT) ucg.setColor(0, 245, 65, 75);
  else if (displayHealthState == DISPLAY_WAIT) ucg.setColor(0, 255, 190, 45);
  else ucg.setColor(0, 50, 220, 125);
}

void drawHealthIndicator() {
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(0, 0, ucg.getWidth(), 21);
  setHealthColor();
  ucg.drawBox(2, 3, 5, 17);
  ucg.setFont(ucg_font_7x13_mr);
  ucg.setColor(0, 130, 190, 215);
  ucg.setPrintPos(co2RangeWrapLatched ? 5 : 11, 16);
  ucg.print(co2RangeWrapLatched ? F("BRUTO ppm") : F("CO2 ppm"));
  char bootCountText[12];
  bootCountText[0] = 'R';
  ltoa(eeprom_contador_int, bootCountText + 1, 10);
  ucg.setColor(0, 230, 235, 240);
  ucg.setPrintPos(ucg.getWidth() - ucg.getStrWidth(bootCountText) - 5, 16);
  ucg.print(bootCountText);
}

void drawDisplayFrame() {
  ucg.clearScreen();
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(0, 0, ucg.getWidth(), ucg.getHeight());
  drawHealthIndicator();
  ucg.setFont(ucg_font_7x13_mr);
  ucg.setColor(0, 130, 190, 215);
  ucg.setPrintPos(73, 91); ucg.print(F("ppm/min"));
  ucg.setColor(0, 150, 200, 225);
  ucg.setPrintPos(5, 59); ucg.print(F("TEMP"));
  ucg.setPrintPos(66, 59); ucg.print(F("UMID"));
  ucg.setPrintPos(5, 91); ucg.print(F("INT"));
  ucg.setColor(0, 45, 65, 82); ucg.drawHLine(8, 116, 112);
  drawCo2Icon(11, 120, botao_co2_onoff, false, 0);
  drawHeaterIcon(53, 121, botao_aquecedor_onoff, false, 0);
  drawFanIcon(98, 120, ventilador_status, ventilador_status != 0, activityIconFrame % 12);
  ucg.setFont(ucg_font_7x13_mr);
  ucg.setFont(ucg_font_inr16_mn);
  displayCacheValid = false;
}

void formatTenths(int16_t value, char *text) {
  if (value == -32768) {
    strcpy_P(text, PSTR("--.- C"));
    return;
  }
  int32_t magnitude = value < 0 ? -(int32_t)value : value;
  char whole[6];
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

void drawTextChanges(char *previous, const char *next, uint8_t x, uint8_t baseline,
                     uint8_t fieldTop, uint8_t fieldHeight, uint8_t fieldWidth,
                     uint8_t bgR, uint8_t bgG, uint8_t bgB,
                     uint8_t fgR, uint8_t fgG, uint8_t fgB) {
  uint8_t oldLength = strlen(previous);
  uint8_t newLength = strlen(next);
  bool redrawWhole = !displayCacheValid || oldLength != newLength ||
                     ucg.getStrWidth(previous) != ucg.getStrWidth(next);
  if (redrawWhole) {
    ucg.setColor(0, bgR, bgG, bgB);
    ucg.drawBox(x - 1, fieldTop, fieldWidth, fieldHeight);
    ucg.setColor(0, fgR, fgG, fgB);
    ucg.setPrintPos(x, baseline);
    ucg.print(next);
  } else {
    char prefix[8];
    char glyph[2] = {' ', '\0'};
    for (uint8_t i = 0; i < newLength; i++) {
      if (previous[i] == next[i]) continue;
      memcpy(prefix, next, i);
      prefix[i] = '\0';
      glyph[0] = previous[i];
      ucg_int_t oldWidth = ucg.getStrWidth(glyph);
      glyph[0] = next[i];
      ucg_int_t newWidth = ucg.getStrWidth(glyph);
      ucg_int_t cellWidth = oldWidth > newWidth ? oldWidth : newWidth;
      if (cellWidth < 1) cellWidth = 1;
      ucg_int_t glyphX = x + ucg.getStrWidth(prefix);
      ucg.setColor(0, bgR, bgG, bgB);
      ucg.drawBox(glyphX, fieldTop, cellWidth + 1, fieldHeight);
      ucg.setColor(0, fgR, fgG, fgB);
      ucg.setPrintPos(glyphX, baseline);
      ucg.print(next[i]);
    }
  }
  strncpy(previous, next, 7);
  previous[7] = '\0';
}

void renderDisplay(float temperature, float humidity, float internalTemperature, bool co2Valid) {
  bool co2AtTarget = co2Valid && CO2i >= CO2_CONTROL_MIN_PPM && CO2i <= CO2_CONTROL_MAX_PPM;
  bool temperatureAtTarget = !isnan(temperature) &&
                             temperature >= TEMPERATURE_GOOD_MIN && temperature <= TEMPERATURE_GOOD_MAX;
  uint8_t conditionsAtTarget = (co2AtTarget ? 1 : 0) + (temperatureAtTarget ? 1 : 0);
  int8_t healthState = conditionsAtTarget == 0 ? DISPLAY_FAULT :
                       (conditionsAtTarget == 1 ? DISPLAY_WAIT : DISPLAY_READY);
  int8_t rangeLockState = co2RangeWrapLatched ? 1 : 0;
  if (healthState != displayHealthState || rangeLockState != displayCo2RangeLock) {
    displayHealthState = healthState;
    displayCo2RangeLock = rangeLockState;
    drawHealthIndicator();
  }
  int16_t tempTenths = isnan(temperature) ? -32768 : (int16_t)(temperature * 10.0f + (temperature >= 0 ? 0.5f : -0.5f));
  int16_t humidityPercent = isnan(humidity) ? -32768 : (int16_t)(humidity + (humidity >= 0 ? 0.5f : -0.5f));
  int16_t internalTempTenths = isnan(internalTemperature) ? -32768 : (int16_t)(internalTemperature * 10.0f + (internalTemperature >= 0 ? 0.5f : -0.5f));
  const uint8_t bgR = 8, bgG = 18, bgB = 30;
  int8_t co2Quality = !co2Valid ? 0 : (co2AtTarget ? 1 : -1);
  int8_t tempQuality = isnan(temperature) ? 0 : (temperatureAtTarget ? 1 : -1);

  if (!displayCacheValid || displayCo2Ppm != CO2i || displayCo2Quality != co2Quality) {
    // Mantém os ppm grandes com a fonte numérica compacta do Uno.
    ucg.setFont(ucg_font_inr16_mn);
    char nextCo2Text[8];
    if (CO2i >= 0) ltoa(CO2i, nextCo2Text, 10);
    else strcpy_P(nextCo2Text, PSTR("---"));
    if (displayCo2Quality != co2Quality) displayCo2Text[0] = '\0';
    uint8_t co2R = co2Quality == 1 ? 70 : (co2Quality == 0 ? 255 : 255);
    uint8_t co2G = co2Quality == 1 ? 235 : (co2Quality == 0 ? 190 : 100);
    uint8_t co2B = co2Quality == 1 ? 145 : (co2Quality == 0 ? 45 : 90);
    drawTextChanges(displayCo2Text, nextCo2Text, 5, 45, 20, 30, 120,
                    bgR, bgG, bgB, co2R, co2G, co2B);
    displayCo2Ppm = CO2i;
    displayCo2Quality = co2Quality;
  }

  bool co2RateValid = co2RatePpmMinReady;
  int32_t shownCo2Rate = co2RateValid ? co2RatePpmMin : 0;
  if (!displayCacheValid || displayCo2RatePpmMin != shownCo2Rate || displayCo2RateReady != co2RateValid) {
    char nextRateText[8];
    formatPpmPerMinute(shownCo2Rate, co2RateValid, nextRateText);
    ucg.setFont(ucg_font_7x13_mr);
    uint8_t rateR = !co2RateValid ? 145 : (shownCo2Rate < 0 ? 255 : (shownCo2Rate > 0 ? 120 : 75));
    uint8_t rateG = !co2RateValid ? 155 : (shownCo2Rate < 0 ? 115 : (shownCo2Rate > 0 ? 215 : 220));
    uint8_t rateB = !co2RateValid ? 165 : (shownCo2Rate < 0 ? 75 : (shownCo2Rate > 0 ? 250 : 145));
    drawTextChanges(displayCo2RateText, nextRateText, 73, 109, 94, 18, 54,
                    bgR, bgG, bgB, rateR, rateG, rateB);
    displayCo2RatePpmMin = shownCo2Rate;
    displayCo2RateReady = co2RateValid;
  }

  ucg.setFont(ucg_font_7x13_mr);
  if (!displayCacheValid || displayTempTenths != tempTenths || displayTempQuality != tempQuality) {
    char nextTempText[8];
    formatTenths(tempTenths, nextTempText);
    if (displayTempQuality != tempQuality) displayTempText[0] = '\0';
    uint8_t tempR = tempQuality == 1 ? 230 : 255;
    uint8_t tempG = tempQuality == 1 ? 235 : (tempQuality == 0 ? 190 : 100);
    uint8_t tempB = tempQuality == 1 ? 240 : (tempQuality == 0 ? 45 : 90);
    drawTextChanges(displayTempText, nextTempText, 5, 77, 62, 18, 58,
                    bgR, bgG, bgB, tempR, tempG, tempB);
    displayTempTenths = tempTenths;
    displayTempQuality = tempQuality;
  }
  if (!displayCacheValid || displayHumidityPercent != humidityPercent) {
    char nextHumidityText[8];
    if (humidityPercent == -32768) strcpy_P(nextHumidityText, PSTR("-- %"));
    else {
      itoa(humidityPercent, nextHumidityText, 10);
      strcat_P(nextHumidityText, PSTR(" %"));
    }
    drawTextChanges(displayHumidityText, nextHumidityText, 66, 77, 62, 18, 59,
                    bgR, bgG, bgB, 230, 235, 240);
    displayHumidityPercent = humidityPercent;
  }
  if (!displayCacheValid || displayInternalTempTenths != internalTempTenths) {
    char nextInternalTempText[8];
    formatTenths(internalTempTenths, nextInternalTempText);
    drawTextChanges(displayInternalTempText, nextInternalTempText, 5, 109, 94, 18, 58,
                    bgR, bgG, bgB, 230, 235, 240);
    displayInternalTempTenths = internalTempTenths;
  }
  if (!displayCacheValid || displayCo2Enabled != botao_co2_onoff) {
    bool co2Flowing = digitalRead(CO2PUMP) == LOW;
    drawCo2Icon(11, 120, botao_co2_onoff, co2Flowing, activityIconFrame & 3);
    displayCo2Active = co2Flowing;
    ucg.setColor(0, bgR, bgG, bgB); ucg.drawBox(4, 137, 38, 18);
    ucg.setColor(0, botao_co2_onoff ? 220 : 120, botao_co2_onoff ? 235 : 155, botao_co2_onoff ? 250 : 175);
    ucg.setPrintPos(8, 153); ucg.print(botao_co2_onoff ? F("ON") : F("OFF"));
    displayCo2Enabled = botao_co2_onoff;
  }
  if (!displayCacheValid || displayHeaterEnabled != botao_aquecedor_onoff) {
    bool heating = digitalRead(HEATER) == LOW;
    drawHeaterIcon(53, 121, botao_aquecedor_onoff, heating, activityIconFrame & 3);
    displayHeaterActive = heating;
    ucg.setColor(0, bgR, bgG, bgB); ucg.drawBox(46, 137, 38, 18);
    ucg.setColor(0, botao_aquecedor_onoff ? 220 : 120, botao_aquecedor_onoff ? 235 : 155, botao_aquecedor_onoff ? 250 : 175);
    ucg.setPrintPos(52, 153); ucg.print(botao_aquecedor_onoff ? F("ON") : F("OFF"));
    displayHeaterEnabled = botao_aquecedor_onoff;
  }
  if (!displayCacheValid || displayFanOn != ventilador_status) {
    drawFanIcon(98, 120, ventilador_status, ventilador_status != 0, activityIconFrame % 12);
    ucg.setColor(0, bgR, bgG, bgB); ucg.drawBox(88, 137, 38, 18);
    ucg.setColor(0, ventilador_status ? 220 : 120, ventilador_status ? 235 : 155, ventilador_status ? 250 : 175);
    ucg.setPrintPos(98, 153); ucg.print(ventilador_status ? F("ON") : F("OFF"));
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
  Serial.print(F(",temp_c=")); printFixed(dht.readTemperature(), 1);
  Serial.print(F(",humidity_pct=")); printFixed(dht.readHumidity(), 1);
  Serial.print(F(",internal_temp_c=")); printFixed(dhtint.readTemperature(), 1);
  Serial.print(F(",co2_enabled=")); Serial.print(botao_co2_onoff);
  Serial.print(F(",heater_enabled=")); Serial.print(botao_aquecedor_onoff);
  Serial.print(F(",fan_on=")); Serial.print(ventilador_status);
  Serial.print(F(",valve_open=")); Serial.print(digitalRead(CO2PUMP) == LOW ? 1 : 0);
  Serial.print(F(",heater_on=")); Serial.print(digitalRead(HEATER) == LOW ? 1 : 0);
  Serial.print(F(",heater_pid_demand_ms=")); Serial.print(heaterPidDemandMs);
  Serial.print(F(",heater_temp_rate_c_min=")); printFixed(heaterTempRateCPerMin, 2);
  Serial.print(F(",pump_wait_cycles=")); Serial.print(contador_pomp);
  Serial.print(F(",rate_ppm_s=")); printFixed(co2Rate, 2);
  Serial.print(F(",rate_ppm_min_valid=")); Serial.print(co2RatePpmMinReady ? 1 : 0);
  Serial.print(F(",rate_ppm_min=")); Serial.print(co2RatePpmMin);
  Serial.print(F(",trend_ready=")); Serial.println(co2TrendReady && contador_pomp == 0 ? 1 : 0);
}

bool manualCo2Pulse(const char *source, uint16_t pulseMs = MANUAL_CO2_PULSE_MS) {
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
  co2RateAtPulsePpmMin = co2RatePpmMinReady ? co2RatePpmMin : 0;
  if (co2RateAtPulsePpmMin < -5000) co2RateAtPulsePpmMin = -5000;
  if (co2RateAtPulsePpmMin > 5000) co2RateAtPulsePpmMin = 5000;
  co2DoseResponsePending = co2BaselineReady;
  maxRate = 0;
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
    else Serial.println(F("ERR,CO2_RANGE_LOCKED; send CO2 ACK after external verification"));
  } else if (strcmp_P(serialCommandBuffer, PSTR("CO2 ACK")) == 0) {
    setCo2Enabled(false);
    EEPROM.update(EEPROM_CO2_RANGE_LOCK, 0);
    co2RangeWrapLatched = false;
    mySensorCO2.rawLoggingEnabled = false;
    co2RawReferenceReady = false;
    co2ReferenceReady = false;
    Serial.println(F("ACK,CO2,RANGE_UNLOCKED_AUTO_OFF"));
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
    Serial.println(F("ACK,HEAT,ON"));
  } else if (strcmp_P(serialCommandBuffer, PSTR("HEAT OFF")) == 0) {
    setHeaterEnabled(false);
    Serial.println(F("ACK,HEAT,OFF"));
  } else if (serialCommandLength > 0) {
    Serial.println(F("ERR,UNKNOWN_COMMAND; send HELP"));
  }
}

bool setCo2Enabled(bool enabled) {
  if (enabled && co2RangeWrapLatched) return false;
  int newState = enabled ? 1 : 0;
  if (botao_co2_onoff != newState) {
    botao_co2_onoff = newState;
  }
  if (!enabled) digitalWrite(CO2PUMP, HIGH);
  return true;
}

void setHeaterEnabled(bool enabled) {
  int newState = enabled ? 1 : 0;
  if (botao_aquecedor_onoff != newState) {
    botao_aquecedor_onoff = newState;
  }
  if (!enabled && digitalRead(HEATER) == LOW) {
    digitalWrite(HEATER, HIGH);
    heaterLastTransitionAt = millis();
    heaterPidDemandMs = 0;
  }
  if (!enabled) heaterPidIntegralMs = 0.0f;
}

void controlHeater(float temperature, unsigned long now) {
  bool heaterOn = digitalRead(HEATER) == LOW;
  bool temperatureFault = isnan(temperature) ||
                          temperature >= HEATER_EMERGENCY_CUTOFF;
  if (temperatureFault &&
      (botao_aquecedor_onoff != 0 || botao_co2_onoff != 0 || heaterOn)) {
    Serial.println(F("EVT,SAFE_OFF"));
    setHeaterEnabled(false);
    setCo2Enabled(false);
    heaterOn = false;
  }
  if (botao_aquecedor_onoff != 1 || temperatureFault) {
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
    // Smooth the 30-second DHT22 trend so one 0.1 C quantization step does not
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

  bool safeToHeat = temperature <= HEATER_SETPOINT_C &&
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

void serviceInputsForTwoSeconds(float temperature) {
  unsigned long started = millis();
  while (millis() - started < 2000UL) {
    unsigned long now = millis();
    controlHeater(temperature, now);
    processSerialCommands();
    finishCo2ClickSequenceIfExpired(now);
    bool co2Pressed = updateButtonState(BOTAO_CO2, co2ButtonStable, co2ButtonCandidate, co2ButtonDebounceCount);
    bool heaterPressed = updateButtonState(BOTAO_AQUECEDOR, heaterButtonStable, heaterButtonCandidate, heaterButtonDebounceCount);
    serviceActivityIconAnimation();
    bool bothPressed = co2ButtonStable && heaterButtonStable;
    if (bothPressed && !bothButtonsStable) {
      Serial.println(F("EVENT,both_buttons_pressed"));
      if (co2ClickCount > 0) setCo2Enabled(co2ModeAtClickSequence);
      co2ClickCount = 0;
      reinitializeScreen();
      eeprom_contador_int = 0;
      EEPROM.put(EEPROM_CONTADOR, eeprom_contador_int);
    } else if (!bothPressed) {
      if (co2Pressed) handleCo2ButtonClick(now);
      if (heaterPressed) {
        setHeaterEnabled(!botao_aquecedor_onoff);
        Serial.print(F("EVENT,heater_toggle,button,")); Serial.println(botao_aquecedor_onoff);
      }
    }
    bothButtonsStable = bothPressed;
    delay(20);
  }
}

void finishCo2ClickSequenceIfExpired(unsigned long now) {
  if (co2ClickCount > 0 && now - co2ClickSequenceStart >= 3000UL) finishCo2ClickSequence();
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
  // Usar toda a dose proporcional de uma vez causou ultrapassagem observada;
  // aplicar 1/6 do déficit por ciclo mantém o ajuste adaptativo e reduz o risco.
  int32_t tempoValvula = ppmNecessario * 100L /
                         (ganhoPpmPorMsX100 * CO2_DOSE_FRACTION_DENOMINATOR);
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
