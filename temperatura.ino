#include <Arduino.h>
#include <SoftwareSerial.h>     
#include <SPI.h>
#include "Ucglib.h"
#include <NDIRZ16.h>
#include <avr/wdt.h>
#include <EEPROM.h>
#include <avr/pgmspace.h>
#include <math.h>
#include <string.h>

#include <Adafruit_Sensor.h>
#include <DHT.h>
#include <DHT_U.h>

//#define ERROR_LOG_ADDRESS 0 // EEPROM address to store error log
#define EEPROM_CO2 0
#define EEPROM_AQUECIMENTO 12
#define EEPROM_CONTADOR 24

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
#define CO2_SENSOR_PROTOCOL_MAX_PPM 65535L
#define CO2_GOOD_MIN_PPM 48000L
#define TEMPERATURE_LIMIT 37
#define TEMPERATURE_GOOD_MIN 36.5
#define TEMPERATURE_GOOD_MAX 37.5
#define POMP_WAITING_TIME 30 // Cerca de 1 minuto com o ciclo atual de 2 s para o MH-Z perceber o pulso
#define MAX_INTERNAL_TEMP 30 // Temperatura maxima antes de ligar o ventilador

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
int32_t eeprom_contador_int = 0;
int ventilador_status = 0;
bool co2ReferenceReady = false;
bool co2BaselineReady = false;
bool co2TrendReady = false;
bool serialHeaderPrinted = false;
bool lastCo2ReadingValid = false;
bool co2RangeWrapLatched = false;
bool co2RawReferenceReady = false;
bool displayCacheValid = false;
int32_t displayCo2Ppm = -2;
int16_t displayTempTenths = 32767;
int16_t displayHumidityPercent = 32767;
int16_t displayInternalTempTenths = 32767;
char displayCo2Text[8] = "";
char displayTempText[8] = "";
char displayHumidityText[8] = "";
char displayInternalTempText[8] = "";
int8_t displayCo2Enabled = -1;
int8_t displayHeaterEnabled = -1;
int8_t displayFanOn = -1;
int8_t displayResponseObserved = -1;
unsigned long lastValidCo2Time = 0;
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
const int DELAY_MAXIMO = 60;      // ms
const int DELAY_MINIMO = 1;       // ms
const int MANUAL_CO2_PULSE_MS = 5; // Pulso curto já citado como referência experimental
#define DISPLAY_FAULT 0
#define DISPLAY_WAIT 1
#define DISPLAY_READY 2
int8_t displayHealthState = DISPLAY_WAIT;
int32_t delayProporcionalAnt = 1;     // Define o delay inicial de abertura da valvula
// const float fatorProximidade = 0.01; // Ajuste este fator para calibrar o impacto da proximidade
bool first_pomp = true; // need to be set so the first pomp uses the minimal delay

// Variáveis para calcular a média de aumento ou queda de CO2 por minuto
int32_t co2AccumulatedChange = 0; // Acumula as mudanças de CO2
unsigned long lastMinuteTime = 0; // Armazena o tempo do último cálculo de média
const unsigned long oneMinuteInterval = 60000; // Intervalo de um minuto em milissegundos

// Variáveis globais para aprendizado adaptativo
// float media_eficiencia = 0.0;
// int contagem_aberturas = 0;

void setup()
{  
    Serial.begin(9600);                                     // Device to serial monitor feedback

    // -------------------- DEBUG --------------------------

    EEPROM.get(EEPROM_AQUECIMENTO, botao_aquecedor_onoff);
    EEPROM.get(EEPROM_CO2, botao_co2_onoff);
    Serial.print(F("PreCO2: "));
    Serial.print(botao_co2_onoff);
    Serial.print(F(" PreTemp: "));
    Serial.println(botao_aquecedor_onoff);

    EEPROM.get(EEPROM_CONTADOR, eeprom_contador_int);
    eeprom_contador_int++;
    EEPROM.put(EEPROM_CONTADOR, eeprom_contador_int);
    Serial.print(F("BOOT_COUNT,"));
    Serial.println(eeprom_contador_int);
   
    
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
    playIntroDna();
    drawDisplayFrame();
    contador_pomp = POMP_WAITING_TIME;
    Serial.println(F("Wait 10 seconds for the sensor to start up"));
//    if (MCUSR & (1 << WDRF)) {
//      Serial.println("Watchdog reset detected.");
//      EEPROM.put(ERROR_LOG_ADDRESS, "Watchdog reset detected."); // Optionally log to EEPROM
//    }
    delay(10000);   
    // Disable auto-calibration
  disableAutoCalibration();

  // Verify if auto-calibration is disabled
  verifyAutoCalibration();
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
      if (co2RawReferenceReady && lastCo2RawPpm >= 60000 && sensorPpm <= 4095 &&
          lastCo2RawPpm - sensorPpm > 55000) {
        co2RangeWrapLatched = true;
        Serial.println(F("EVENT,co2_protocol_rollover_suspected,control_locked_until_restart"));
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
          co2AccumulatedChange += co2Delta;
          co2TrendReady = true;
        } else {
          co2Rate = 0;
        }
      } else {
        co2ReferenceReady = true;
        co2Rate = 0;
      }
      lastValidCo2Time = currentTime;
      if (co2BaselineReady) {
        int32_t increaseSincePump = CO2i - co2_before_pump;
        if (increaseSincePump > max_co2_increase) max_co2_increase = increaseSincePump;
      } else {
        co2_before_pump = CO2i;
        co2BaselineReady = true;
      }
    } else {
      co2Rate = 0;
      co2ReferenceReady = false;
      co2TrendReady = false;
    }
    // float averageChangePerMinute = 0.0;
    // Verificar se passou um minuto para calcular a média
    if (currentTime - lastMinuteTime >= oneMinuteInterval) {
        Serial.print(F("Média de aumento/queda de CO2 por minuto: "));
        Serial.print(co2AccumulatedChange);
        Serial.println(F(" ppm/min"));

        // Reiniciar acumulador e tempo
        co2AccumulatedChange = 0;
        lastMinuteTime = currentTime;
    }
    int32_t delayProporcional = validCo2
      ? calcularDelayProporcional(CO2i, CO2_TARGET_PPM, delayProporcionalAnt, max_co2_increase, co2TrendReady && contador_pomp == 0)
      : DELAY_MINIMO;

    
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    float t_interna = dhtint.readTemperature();      
    processSerialCommands();
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

    if(contador_pomp < 0){
      contador_pomp = 0;
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

    if (validCo2 && CO2i < CO2_TARGET_PPM && botao_co2_onoff == 1 &&
        contador_pomp == 0 && co2ClickCount == 0) {
      co2_before_pump = CO2i;
      co2BaselineReady = true;
      int32_t pulseMs;
      if (first_pomp) {
        first_pomp = false;
        pulseMs = MANUAL_CO2_PULSE_MS;
        Serial.print(F("EVENT,co2_pulse,first,ms,"));
      } else if (max_co2_increase <= 8) {
        pulseMs = delayProporcionalAnt * 2;
        if (pulseMs > DELAY_MAXIMO) pulseMs = DELAY_MAXIMO;
        Serial.print(F("EVENT,co2_pulse,ramp,ms,"));
      } else {
        pulseMs = delayProporcional;
        Serial.print(F("EVENT,co2_pulse,ms,"));
      }
      if (pulseMs > DELAY_MAXIMO) pulseMs = DELAY_MAXIMO;
      if (pulseMs < DELAY_MINIMO) pulseMs = DELAY_MINIMO;
      Serial.println(pulseMs);
      digitalWrite(CO2PUMP, LOW);
      delay(pulseMs);
      digitalWrite(CO2PUMP, HIGH);
      delayProporcionalAnt = pulseMs;
      max_co2_increase = 0;
      co2TrendReady = false;
      contador_pomp = POMP_WAITING_TIME;
      maxRate = 0;
    } else {
      digitalWrite(CO2PUMP, HIGH);
    }

    if(t < TEMPERATURE_LIMIT){ 
      if(botao_aquecedor_onoff == 1){
        digitalWrite(HEATER,LOW);
      } else {
        digitalWrite(HEATER,HIGH);
      }
    } else {
      digitalWrite(HEATER,HIGH);
    }
    renderDisplay(t, h, t_interna, validCo2);
    if (!serialHeaderPrinted) {
      Serial.println(F("DATA,ms,co2_ppm,co2_valid,temp_c,humidity_pct,internal_temp_c,co2_enabled,heater_enabled,heater_on,fan_on,valve_open,valve_ms,rate_ppm_s,max_rate_ppm_s,delta_ppm,max_co2_rise_since_pump_ppm,pump_wait_cycles,trend_ready"));
      serialHeaderPrinted = true;
    }
    Serial.print(F("DATA,")); Serial.print(currentTime); Serial.print(','); Serial.print(CO2i); Serial.print(','); Serial.print(validCo2 ? 1 : 0);
    Serial.print(','); Serial.print(t); Serial.print(','); Serial.print(h); Serial.print(','); Serial.print(t_interna);
    Serial.print(','); Serial.print(botao_co2_onoff); Serial.print(','); Serial.print(botao_aquecedor_onoff); Serial.print(',');
    Serial.print(digitalRead(HEATER) == LOW ? 1 : 0); Serial.print(','); Serial.print(ventilador_status); Serial.print(',');
    Serial.print(digitalRead(CO2PUMP) == LOW ? 1 : 0); Serial.print(','); Serial.print(delayProporcional); Serial.print(',');
    Serial.print(co2Rate, 2); Serial.print(','); Serial.print(maxRate, 2); Serial.print(','); Serial.print(co2Delta); Serial.print(',');
    Serial.print(max_co2_increase); Serial.print(','); Serial.print(contador_pomp); Serial.print(','); Serial.println(co2TrendReady && contador_pomp == 0 ? 1 : 0);

    contador_pomp = contador_pomp -1;
    serviceInputsForTwoSeconds();
    // delay(60000);
}



void reinitializeScreen() {
    ucg.begin(UCG_FONT_MODE_TRANSPARENT);
    ucg.setRotate180();
    drawDisplayFrame();
}

void drawLogoStroke(int16_t x1, int16_t y1, int16_t x2, int16_t y2,
                    uint8_t r, uint8_t g, uint8_t b) {
  ucg.setColor(0, r, g, b);
  ucg.drawLine(x1, y1, x2, y2);
  ucg.drawLine(x1 + 1, y1, x2 + 1, y2);
  ucg.drawLine(x1 - 1, y1, x2 - 1, y2);
}

void playIntroDna() {
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(0, 0, ucg.getWidth(), ucg.getHeight());
  static const int8_t strandA[] PROGMEM = {64, 82, 94, 96, 87, 70, 50, 36, 32, 40, 57, 77, 92, 96, 88, 70, 50};
  static const int8_t strandB[] PROGMEM = {64, 46, 34, 32, 41, 58, 78, 92, 96, 88, 71, 51, 36, 32, 40, 58, 78};

  // Large double helix with base pairs visible across the full display.
  for (uint8_t i = 0; i < 16; i++) {
    int16_t y = 14 + i * 8;
    int16_t ax = pgm_read_byte(&strandA[i]);
    int16_t bx = pgm_read_byte(&strandB[i]);
    int16_t nextY = y + 8;
    int16_t nextAx = pgm_read_byte(&strandA[i + 1]);
    int16_t nextBx = pgm_read_byte(&strandB[i + 1]);
    drawLogoStroke(ax, y, nextAx, nextY, 93, 89, 255);
    drawLogoStroke(bx, y, nextBx, nextY, 156, 104, 255);
    if ((i & 1) == 0) {
      ucg.setColor(0, 115, 205, 250);
      ucg.drawLine(ax, y, bx, y);
    }
  }
  delay(350);
}

void drawCo2Icon(uint8_t x, uint8_t y, bool enabled) {
  ucg.setColor(0, enabled ? 235 : 125, enabled ? 248 : 145, enabled ? 255 : 160);
  ucg.drawCircle(x + 5, y + 5, 4, UCG_DRAW_ALL);
  ucg.drawCircle(x + 16, y + 2, 2, UCG_DRAW_ALL);
  ucg.drawCircle(x + 17, y + 12, 3, UCG_DRAW_ALL);
  ucg.drawLine(x + 9, y + 4, x + 14, y + 3);
  ucg.drawLine(x + 9, y + 7, x + 14, y + 10);
}

void drawHeaterIcon(uint8_t x, uint8_t y, bool enabled) {
  ucg.setColor(0, enabled ? 255 : 145, enabled ? 195 : 155, enabled ? 65 : 165);
  ucg.drawLine(x, y + 3, x + 4, y + 3);
  ucg.drawLine(x + 4, y + 3, x + 7, y + 10);
  ucg.drawLine(x + 7, y + 10, x + 11, y + 3);
  ucg.drawLine(x + 11, y + 3, x + 15, y + 10);
  ucg.drawLine(x + 15, y + 10, x + 19, y + 3);
}

void drawFanIcon(uint8_t x, uint8_t y, bool enabled) {
  ucg.setColor(0, enabled ? 75 : 145, enabled ? 210 : 155, enabled ? 255 : 165);
  ucg.drawCircle(x + 8, y + 7, 2, UCG_DRAW_ALL);
  ucg.drawLine(x + 8, y + 5, x + 8, y);
  ucg.drawLine(x + 10, y + 7, x + 15, y + 5);
  ucg.drawLine(x + 8, y + 9, x + 8, y + 14);
  ucg.drawLine(x + 6, y + 7, x + 1, y + 9);
}

void setHealthColor() {
  if (displayHealthState == DISPLAY_FAULT) ucg.setColor(0, 245, 65, 75);
  else if (displayHealthState == DISPLAY_WAIT) ucg.setColor(0, 255, 190, 45);
  else ucg.setColor(0, 50, 220, 125);
}

void drawHealthIndicator() {
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(0, 0, ucg.getWidth(), 160);
  setHealthColor();
  ucg.drawBox(0, 0, 5, ucg.getHeight());
  ucg.drawBox(8, 4, 112, 2);
  ucg.setFont(ucg_font_7x13_mr);
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(8, 4, 46, 15);
  ucg.setColor(0, 245, 250, 255);
  ucg.setPrintPos(10, 15); ucg.print(displayHealthState == DISPLAY_FAULT ? F("2 FORA") : (displayHealthState == DISPLAY_WAIT ? F("1 FORA") : F("OK")));
  ucg.setColor(0, 130, 190, 215);
  ucg.setPrintPos(78, 15); ucg.print(F("CO2 ppm"));
}

void drawDisplayFrame() {
  ucg.clearScreen();
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(0, 0, ucg.getWidth(), ucg.getHeight());
  drawHealthIndicator();
  ucg.setColor(0, 150, 200, 225);
  ucg.setPrintPos(5, 59); ucg.print(F("TEMP"));
  ucg.setPrintPos(66, 59); ucg.print(F("UMID"));
  ucg.setPrintPos(5, 91); ucg.print(F("INT"));
  ucg.setColor(0, 45, 65, 82); ucg.drawHLine(8, 114, 112);
  drawCo2Icon(7, 122, botao_co2_onoff);
  drawHeaterIcon(49, 123, botao_aquecedor_onoff);
  drawFanIcon(91, 122, ventilador_status);
  ucg.setFont(ucg_font_7x13_mr);
  ucg.setColor(0, 180, 200, 215);
  ucg.setPrintPos(29, 143); ucg.print(botao_co2_onoff ? F("ON") : F("OFF"));
  ucg.setPrintPos(71, 143); ucg.print(botao_aquecedor_onoff ? F("ON") : F("OFF"));
  ucg.setPrintPos(111, 143); ucg.print(ventilador_status ? F("ON") : F("OFF"));
  ucg.setColor(0, 130, 155, 175);
  ucg.setPrintPos(12, 158); ucg.print(F("CONTROLES"));
  ucg.setPrintPos(85, 158); ucg.print(co2TrendReady && contador_pomp == 0 ? F("CO2 OK") : F("CO2 WAIT"));
  ucg.setFont(ucg_font_inr16_mr);
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
  bool co2AtTarget = co2Valid && CO2i >= CO2_GOOD_MIN_PPM && CO2i <= CO2_TARGET_PPM;
  bool temperatureAtTarget = !isnan(temperature) &&
                             temperature >= TEMPERATURE_GOOD_MIN && temperature <= TEMPERATURE_GOOD_MAX;
  uint8_t conditionsAtTarget = (co2AtTarget ? 1 : 0) + (temperatureAtTarget ? 1 : 0);
  int8_t healthState = conditionsAtTarget == 0 ? DISPLAY_FAULT :
                       (conditionsAtTarget == 1 ? DISPLAY_WAIT : DISPLAY_READY);
  if (healthState != displayHealthState) {
    displayHealthState = healthState;
    drawHealthIndicator();
    displayCo2Text[0] = '\0';
    displayCo2Ppm = -2;
  }
  bool responseObserved = co2TrendReady && contador_pomp == 0;
  int16_t tempTenths = isnan(temperature) ? -32768 : (int16_t)(temperature * 10.0f + (temperature >= 0 ? 0.5f : -0.5f));
  int16_t humidityPercent = isnan(humidity) ? -32768 : (int16_t)(humidity + (humidity >= 0 ? 0.5f : -0.5f));
  int16_t internalTempTenths = isnan(internalTemperature) ? -32768 : (int16_t)(internalTemperature * 10.0f + (internalTemperature >= 0 ? 0.5f : -0.5f));
  const uint8_t bgR = 8, bgG = 18, bgB = 30;

  if (!displayCacheValid || displayCo2Ppm != (co2Valid ? CO2i : -1)) {
    ucg.setFont(ucg_font_inr16_mr);
    char nextCo2Text[8];
    if (co2Valid) ltoa(CO2i, nextCo2Text, 10);
    else strcpy_P(nextCo2Text, PSTR("---"));
    drawTextChanges(displayCo2Text, nextCo2Text, 5, 45, 20, 30, 120,
                    displayHealthState == DISPLAY_FAULT ? 180 : (displayHealthState == DISPLAY_WAIT ? 235 : 0),
                    displayHealthState == DISPLAY_FAULT ? 8 : (displayHealthState == DISPLAY_WAIT ? 165 : 115),
                    displayHealthState == DISPLAY_FAULT ? 12 : (displayHealthState == DISPLAY_WAIT ? 0 : 30),
                    235, 248, 255);
    displayCo2Ppm = co2Valid ? CO2i : -1;
  }

  ucg.setFont(ucg_font_7x13_mr);
  if (!displayCacheValid || displayTempTenths != tempTenths) {
    char nextTempText[8];
    formatTenths(tempTenths, nextTempText);
    drawTextChanges(displayTempText, nextTempText, 5, 77, 62, 18, 58,
                    bgR, bgG, bgB, 230, 235, 240);
    displayTempTenths = tempTenths;
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
    drawCo2Icon(4, 120, botao_co2_onoff);
    ucg.setColor(0, 180, 200, 215); ucg.drawBox(28, 130, 20, 16); ucg.setPrintPos(29, 143); ucg.print(botao_co2_onoff ? F("ON ") : F("OFF"));
    displayCo2Enabled = botao_co2_onoff;
  }
  if (!displayCacheValid || displayHeaterEnabled != botao_aquecedor_onoff) {
    drawHeaterIcon(65, 121, botao_aquecedor_onoff);
    ucg.setColor(0, 180, 200, 215); ucg.drawBox(70, 130, 20, 16); ucg.setPrintPos(71, 143); ucg.print(botao_aquecedor_onoff ? F("ON ") : F("OFF"));
    displayHeaterEnabled = botao_aquecedor_onoff;
  }
  if (!displayCacheValid || displayFanOn != ventilador_status) {
    drawFanIcon(91, 122, ventilador_status);
    ucg.setColor(0, 180, 200, 215); ucg.drawBox(110, 130, 18, 16); ucg.setPrintPos(111, 143); ucg.print(ventilador_status ? F("ON ") : F("OFF"));
    displayFanOn = ventilador_status;
  }
  if (!displayCacheValid || displayResponseObserved != responseObserved) {
    ucg.setColor(0, bgR, bgG, bgB); ucg.drawBox(84, 145, 44, 15);
    ucg.setColor(0, responseObserved ? 60 : 220, responseObserved ? 210 : 175, responseObserved ? 120 : 60);
    ucg.setPrintPos(85, 158); ucg.print(responseObserved ? F("CO2 OK") : F("CO2 WAIT"));
    displayResponseObserved = responseObserved;
  }
  displayCacheValid = true;
}

void printStatus(unsigned long now) {
  Serial.print(F("STATUS,ms=")); Serial.print(now);
  Serial.print(F(",co2_ppm=")); Serial.print(CO2i);
  Serial.print(F(",co2_valid=")); Serial.print(CO2i > 0 && CO2i <= CO2_SENSOR_PROTOCOL_MAX_PPM && !co2RangeWrapLatched ? 1 : 0);
  Serial.print(F(",boot_count=")); Serial.print(eeprom_contador_int);
  Serial.print(F(",temp_c=")); Serial.print(dht.readTemperature());
  Serial.print(F(",humidity_pct=")); Serial.print(dht.readHumidity());
  Serial.print(F(",internal_temp_c=")); Serial.print(dhtint.readTemperature());
  Serial.print(F(",co2_enabled=")); Serial.print(botao_co2_onoff);
  Serial.print(F(",heater_enabled=")); Serial.print(botao_aquecedor_onoff);
  Serial.print(F(",fan_on=")); Serial.print(ventilador_status);
  Serial.print(F(",valve_open=")); Serial.print(digitalRead(CO2PUMP) == LOW ? 1 : 0);
  Serial.print(F(",heater_on=")); Serial.print(digitalRead(HEATER) == LOW ? 1 : 0);
  Serial.print(F(",pump_wait_cycles=")); Serial.print(contador_pomp);
  Serial.print(F(",rate_ppm_s=")); Serial.print(co2Rate, 2);
  Serial.print(F(",trend_ready=")); Serial.println(co2TrendReady && contador_pomp == 0 ? 1 : 0);
}

bool manualCo2Pulse(const char *source) {
  unsigned long now = millis();
  bool freshReading = lastCo2ReadingValid && now - lastValidCo2Time <= 5000UL;
  if ((CO2i > 0 && CO2i >= CO2_TARGET_PPM) || digitalRead(CO2PUMP) == LOW) {
    Serial.println(F("ERR,CO2_PRIME_LIMIT_OR_VALVE_BUSY"));
    return false;
  }
  co2BaselineReady = freshReading && CO2i > 0;
  if (co2BaselineReady) co2_before_pump = CO2i;
  max_co2_increase = 0;
  co2TrendReady = false;
  co2ReferenceReady = freshReading;
  if (freshReading) last_co2i = CO2i;
  delayProporcionalAnt = MANUAL_CO2_PULSE_MS;
  first_pomp = false;
  maxRate = 0;
  digitalWrite(CO2PUMP, LOW);
  delay(MANUAL_CO2_PULSE_MS);
  digitalWrite(CO2PUMP, HIGH);
  contador_pomp = POMP_WAITING_TIME;
  Serial.print(F("EVENT,co2_manual_pulse,")); Serial.print(source); Serial.print(','); Serial.print(MANUAL_CO2_PULSE_MS);
  Serial.print(F("ms,baseline,")); if (co2BaselineReady) Serial.println(F("valid")); else Serial.println(F("pending"));
  return true;
}

void handleSerialCommand() {
  if (strcmp_P(serialCommandBuffer, PSTR("STATUS")) == 0) {
    printStatus(millis());
  } else if (strcmp_P(serialCommandBuffer, PSTR("HELP")) == 0) {
    Serial.println(F("COMMANDS: STATUS, HELP, CO2 ON/OFF/PRIME, HEAT ON/OFF, ALL OFF"));
  } else if (strcmp_P(serialCommandBuffer, PSTR("CO2 ON")) == 0) {
    co2ClickCount = 0; setCo2Enabled(true);
    Serial.println(F("ACK,CO2,ON"));
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

void setCo2Enabled(bool enabled) {
  int newState = enabled ? 1 : 0;
  if (botao_co2_onoff != newState) {
    botao_co2_onoff = newState;
    EEPROM.put(EEPROM_CO2, botao_co2_onoff);
  }
  if (enabled) first_pomp = true;
  else digitalWrite(CO2PUMP, HIGH);
}

void setHeaterEnabled(bool enabled) {
  int newState = enabled ? 1 : 0;
  if (botao_aquecedor_onoff != newState) {
    botao_aquecedor_onoff = newState;
    EEPROM.put(EEPROM_AQUECIMENTO, botao_aquecedor_onoff);
  }
  if (!enabled) digitalWrite(HEATER, HIGH);
}

void finishCo2ClickSequence() {
  if (co2ClickCount == 0) return;
  bool targetState = co2ModeAtClickSequence ^ (co2ClickCount & 1);
  setCo2Enabled(targetState);
  Serial.print(F("EVENT,co2_button_clicks,")); Serial.println(co2ClickCount);
  co2ClickCount = 0;
}

void handleCo2ButtonClick(unsigned long now) {
  if (co2ClickCount == 0) {
    co2ClickSequenceStart = now;
    co2ModeAtClickSequence = botao_co2_onoff;
  }
  co2ClickCount++;
  if (co2ClickCount >= 3) {
    co2ClickCount = 0;
    manualCo2Pulse("button");
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
    processSerialCommands();
    finishCo2ClickSequenceIfExpired(now);
    bool co2Pressed = updateButtonState(BOTAO_CO2, co2ButtonStable, co2ButtonCandidate, co2ButtonDebounceCount);
    bool heaterPressed = updateButtonState(BOTAO_AQUECEDOR, heaterButtonStable, heaterButtonCandidate, heaterButtonDebounceCount);
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

  // Wait for a response (optional, for debugging)
  delay(500);
  while (mySerialCO2.available()) {
    byte response = mySerialCO2.read();
    Serial.print(response, HEX);
    Serial.print(" ");
  }
  Serial.println();
}

void verifyAutoCalibration() {
  // Command to check auto-calibration status
  // byte checkAutoCalib[] = {0xFF, 0x01, 0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x82}; // Adjust checksum as needed
  // mySerialCO2.write(checkAutoCalib, 9);

  // Wait for a response
  delay(500);
  byte response[9];
  int index = 0;
  while (mySerialCO2.available() && index < 9) {
    response[index++] = mySerialCO2.read();
  }

  // Print the response
  Serial.print("Auto-Calibration Response: ");
  for (int i = 0; i < 9; i++) {
    Serial.print(response[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  // Check the auto-calibration status from the response
  if (response[2] == 0x79 && response[3] == 0x00) {
    Serial.println("Auto-calibration is disabled.");
  } else if (response[1] == 0x7D && response[2] == 0x01) {
    Serial.println("Auto-calibration is enabled.");
  } else {
    Serial.println("Unknown response.");
  }
}


// Função para calcular o tempo de abertura
int32_t calcularDelayProporcional(int32_t ppm_atual, int32_t ppm_objetivo, int32_t ms_ultima_vez, int32_t aumento_ultima_vez, bool tendenciaValida) {
  if (!tendenciaValida || ppm_atual <= 0 || ppm_objetivo <= ppm_atual || ms_ultima_vez <= 0 || aumento_ultima_vez <= 0) {
    return DELAY_MINIMO;
  }
  int64_t ppmNecessario = (int64_t)ppm_objetivo - ppm_atual;
  int64_t tempoValvula = ppmNecessario * ms_ultima_vez / aumento_ultima_vez;
  if (tempoValvula < DELAY_MINIMO) return DELAY_MINIMO;
  if (tempoValvula > DELAY_MAXIMO) return DELAY_MAXIMO;
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
