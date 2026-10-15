#include <Arduino.h>
#include <SoftwareSerial.h>     
#include <SPI.h>
#include "Ucglib.h"
#include <NDIRZ16.h>
#include <avr/wdt.h>
#include <EEPROM.h>
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

#define CO2_LIMIT 50000
#define TEMPERATURE_LIMIT 37
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
int32_t eeprom_contador_int = 0;
int ventilador_status = 0;
bool co2ReferenceReady = false;
bool co2BaselineReady = false;
bool co2TrendReady = false;
bool serialHeaderPrinted = false;
bool lastCo2ReadingValid = false;
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
    Serial.print("PreCO2: ");
    Serial.print(botao_co2_onoff);
    Serial.print(" PreTemp: ");
    Serial.println(botao_aquecedor_onoff);

    EEPROM.get(EEPROM_CONTADOR, eeprom_contador_int);
    eeprom_contador_int++;
    EEPROM.put(EEPROM_CONTADOR, eeprom_contador_int);
   
    
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
    drawDisplayFrame();
    contador_pomp = POMP_WAITING_TIME;
    Serial.println("Wait 10 seconds for the sensor to start up");
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
    // Set range to 0-100000 ppm
    // setMeasurementRange100000();
    requestMeasurementRange();
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
    } else {
      CO2i = -1;
      Serial.println("EVENT,co2_sensor_read_failed");
    }
    unsigned long currentTime = millis();
    int32_t co2Delta = 0;
    bool validCo2 = sensorReadOk && CO2i > 0 && CO2i < CO2_LIMIT;
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
        Serial.print("Média de aumento/queda de CO2 por minuto: ");
        Serial.print(co2AccumulatedChange);
        Serial.println(" ppm/min");

        // Reiniciar acumulador e tempo
        co2AccumulatedChange = 0;
        lastMinuteTime = currentTime;
    }
    int32_t delayProporcional = validCo2
      ? calcularDelayProporcional(CO2i, CO2_LIMIT, delayProporcionalAnt, max_co2_increase, co2TrendReady && contador_pomp == 0)
      : DELAY_MINIMO;

    
    float h = dht.readHumidity();
    float t = dht.readTemperature();
    float t_interna = dhtint.readTemperature();      
    processSerialCommands();
    if (validCo2) last_co2i = CO2i;
    // Serial.println(t_interna);
    if(t_interna >= MAX_INTERNAL_TEMP && ventilador_status == 0){
      Serial.println("EVENT,fan,on");
       digitalWrite(VENTILADOR_PIN,LOW);
       ventilador_status = 1;
    } else if (t_interna < (MAX_INTERNAL_TEMP - 1.0) && ventilador_status == 1){
      Serial.println("EVENT,fan,off");
       digitalWrite(VENTILADOR_PIN,HIGH); 
       ventilador_status = 0;
    }

    if(contador_pomp < 0){
      contador_pomp = 0;
    }
    
    if(sensorReadOk && CO2i == 0){
      Serial.println("EVENT,co2_zero_reading,invalid_for_control");
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

    if(CO2i < CO2_LIMIT && CO2i > 0){      
      if(botao_co2_onoff == 1 && contador_pomp == 0 && co2ClickCount == 0){
        if(co2ReferenceReady && CO2i < previousCo2i){ // so adiciona mais CO2 se ele tiver caindo
          // int delayProporcional = calcularDelayProporcional(maxRate, CO2i);
          co2_before_pump = CO2i;
          co2BaselineReady = true;
          digitalWrite(CO2PUMP,LOW);  
          // delay(10);
          if(delayProporcional > DELAY_MAXIMO){
            delayProporcional = DELAY_MAXIMO;
          } else if (delayProporcional < DELAY_MINIMO){
            delayProporcional = DELAY_MINIMO;
          }
          if(first_pomp){
            first_pomp = false;
            delay(DELAY_MINIMO);
            delayProporcionalAnt = DELAY_MINIMO;
            Serial.println("EVENT,co2_pulse,first,min");
          } else {            
            Serial.print("EVENT,co2_pulse,ms,");
            Serial.println(delayProporcional);
            delay(delayProporcional);
            delayProporcionalAnt = delayProporcional;
          }
          max_co2_increase = 0;
          co2TrendReady = false;
          digitalWrite(CO2PUMP,HIGH);
          contador_pomp = POMP_WAITING_TIME;
          reinitializeScreen();
          maxRate = 0;
        } else {
          contador_pomp = 10; // gera mais 10 loops pra poder ver se comeca a cair realmente
          Serial.println("EVENT,co2_rising_or_stable");
        }
      } else {
        digitalWrite(CO2PUMP,HIGH);
      }
    } else {
      digitalWrite(CO2PUMP,HIGH);
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
      Serial.println("DATA,ms,co2_ppm,co2_valid,temp_c,humidity_pct,internal_temp_c,co2_enabled,heater_enabled,heater_on,fan_on,valve_open,valve_ms,rate_ppm_s,max_rate_ppm_s,delta_ppm,max_co2_rise_since_pump_ppm,pump_wait_cycles,trend_ready");
      serialHeaderPrinted = true;
    }
    Serial.print("DATA,"); Serial.print(currentTime); Serial.print(','); Serial.print(CO2i); Serial.print(','); Serial.print(validCo2 ? 1 : 0);
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

void drawDisplayFrame() {
  ucg.clearScreen();
  ucg.setColor(0, 8, 18, 30);
  ucg.drawBox(0, 0, ucg.getWidth(), ucg.getHeight());
  ucg.setFont(ucg_font_7x13_mr);
  ucg.setColor(0, 90, 210, 235);
  ucg.setPrintPos(5, 14); ucg.print("INCUBADORA CO2");
  ucg.setColor(0, 45, 75, 95);
  ucg.drawHLine(4, 20, 120);
  ucg.setColor(0, 135, 175, 205);
  ucg.setPrintPos(5, 31); ucg.print("CO2");
  ucg.setPrintPos(5, 70); ucg.print("TEMP");
  ucg.setPrintPos(66, 70); ucg.print("UMID");
  ucg.setPrintPos(5, 96); ucg.print("INT");
  ucg.setFont(ucg_font_inr16_mr);
}

void renderDisplay(float temperature, float humidity, float internalTemperature, bool co2Valid) {
  bool responseObserved = co2TrendReady && contador_pomp == 0;
  ucg.setFont(ucg_font_inr16_mr);
  ucg.setColor(0, 8, 18, 30); ucg.drawBox(4, 33, 120, 28);
  ucg.setColor(0, 235, 248, 255); ucg.setPrintPos(5, 56);
  if (co2Valid) { ucg.print(CO2i); ucg.print("ppm"); }
  else ucg.print("---");

  ucg.setFont(ucg_font_7x13_mr);
  ucg.setColor(0, 8, 18, 30); ucg.drawBox(4, 72, 120, 18); ucg.drawBox(4, 98, 120, 18);
  ucg.setColor(0, 230, 235, 240);
  ucg.setPrintPos(5, 85); if (isnan(temperature)) ucg.print("--.- C"); else { ucg.print(temperature, 1); ucg.print(" C"); }
  ucg.setPrintPos(66, 85); if (isnan(humidity)) ucg.print("-- %"); else { ucg.print(humidity, 0); ucg.print(" %"); }
  ucg.setPrintPos(5, 111); if (isnan(internalTemperature)) ucg.print("--.- C"); else { ucg.print(internalTemperature, 1); ucg.print(" C"); }

  ucg.setColor(0, 8, 18, 30); ucg.drawBox(4, 119, 120, 26); ucg.drawBox(4, 145, 120, 15);
  ucg.setColor(0, botao_co2_onoff ? 40 : 150, botao_co2_onoff ? 220 : 155, botao_co2_onoff ? 100 : 165);
  ucg.setPrintPos(5, 137); ucg.print(botao_co2_onoff ? "INJ ON" : "INJ OFF");
  ucg.setColor(0, botao_aquecedor_onoff ? 240 : 150, botao_aquecedor_onoff ? 170 : 155, 65);
  ucg.setPrintPos(66, 137); ucg.print(botao_aquecedor_onoff ? "HEAT ON" : "HEAT OFF");
  ucg.setColor(0, ventilador_status ? 45 : 150, ventilador_status ? 200 : 155, ventilador_status ? 255 : 165);
  ucg.setPrintPos(5, 157); ucg.print(ventilador_status ? "FAN ON" : "FAN OFF");
  ucg.setColor(0, responseObserved ? 60 : 220, responseObserved ? 210 : 175, responseObserved ? 120 : 60);
  ucg.setPrintPos(66, 157); ucg.print(responseObserved ? "CO2 OK" : "CO2 WAIT");
}

void printStatus(unsigned long now) {
  Serial.print("STATUS,ms="); Serial.print(now);
  Serial.print(",co2_ppm="); Serial.print(CO2i);
  Serial.print(",co2_valid="); Serial.print(CO2i > 0 && CO2i < CO2_LIMIT ? 1 : 0);
  Serial.print(",temp_c="); Serial.print(dht.readTemperature());
  Serial.print(",humidity_pct="); Serial.print(dht.readHumidity());
  Serial.print(",internal_temp_c="); Serial.print(dhtint.readTemperature());
  Serial.print(",co2_enabled="); Serial.print(botao_co2_onoff);
  Serial.print(",heater_enabled="); Serial.print(botao_aquecedor_onoff);
  Serial.print(",fan_on="); Serial.print(ventilador_status);
  Serial.print(",valve_open="); Serial.print(digitalRead(CO2PUMP) == LOW ? 1 : 0);
  Serial.print(",heater_on="); Serial.print(digitalRead(HEATER) == LOW ? 1 : 0);
  Serial.print(",pump_wait_cycles="); Serial.print(contador_pomp);
  Serial.print(",rate_ppm_s="); Serial.print(co2Rate, 2);
  Serial.print(",trend_ready="); Serial.println(co2TrendReady && contador_pomp == 0 ? 1 : 0);
}

bool manualCo2Pulse(const char *source) {
  unsigned long now = millis();
  bool freshReading = lastCo2ReadingValid && now - lastValidCo2Time <= 5000UL;
  if ((CO2i > 0 && CO2i >= CO2_LIMIT) || digitalRead(CO2PUMP) == LOW) {
    Serial.println("ERR,CO2_PRIME_LIMIT_OR_VALVE_BUSY");
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
  Serial.print("EVENT,co2_manual_pulse,"); Serial.print(source); Serial.print(','); Serial.print(MANUAL_CO2_PULSE_MS);
  Serial.print("ms,baseline,"); Serial.println(co2BaselineReady ? "valid" : "pending");
  return true;
}

void handleSerialCommand() {
  if (strcmp(serialCommandBuffer, "STATUS") == 0) {
    printStatus(millis());
  } else if (strcmp(serialCommandBuffer, "HELP") == 0) {
    Serial.println("COMMANDS: STATUS, HELP, CO2 ON/OFF/PRIME, HEAT ON/OFF, ALL OFF");
  } else if (strcmp(serialCommandBuffer, "CO2 ON") == 0) {
    co2ClickCount = 0; setCo2Enabled(true);
    Serial.println("ACK,CO2,ON");
  } else if (strcmp(serialCommandBuffer, "CO2 OFF") == 0 || strcmp(serialCommandBuffer, "ALL OFF") == 0) {
    co2ClickCount = 0; setCo2Enabled(false);
    if (strcmp(serialCommandBuffer, "ALL OFF") == 0) {
      setHeaterEnabled(false);
      Serial.println("ACK,ALL,OFF");
    } else Serial.println("ACK,CO2,OFF");
  } else if (strcmp(serialCommandBuffer, "CO2 PRIME") == 0) {
    if (manualCo2Pulse("serial")) Serial.println("ACK,CO2,PRIME");
  } else if (strcmp(serialCommandBuffer, "HEAT ON") == 0) {
    setHeaterEnabled(true);
    Serial.println("ACK,HEAT,ON");
  } else if (strcmp(serialCommandBuffer, "HEAT OFF") == 0) {
    setHeaterEnabled(false);
    Serial.println("ACK,HEAT,OFF");
  } else if (serialCommandLength > 0) {
    Serial.println("ERR,UNKNOWN_COMMAND; send HELP");
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
  Serial.print("EVENT,co2_button_clicks,"); Serial.println(co2ClickCount);
  co2ClickCount = 0;
}

void handleCo2ButtonClick(unsigned long now) {
  if (co2ClickCount == 0) {
    co2ClickSequenceStart = now;
    co2ModeAtClickSequence = botao_co2_onoff;
  }
  setCo2Enabled(!botao_co2_onoff);
  co2ClickCount++;
  if (co2ClickCount >= 3) {
    setCo2Enabled(co2ModeAtClickSequence);
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
      Serial.println("EVENT,both_buttons_pressed");
      if (co2ClickCount > 0) setCo2Enabled(co2ModeAtClickSequence);
      co2ClickCount = 0;
      reinitializeScreen();
      eeprom_contador_int = 0;
      EEPROM.put(EEPROM_CONTADOR, eeprom_contador_int);
    } else if (!bothPressed) {
      if (co2Pressed) handleCo2ButtonClick(now);
      if (heaterPressed) {
        setHeaterEnabled(!botao_aquecedor_onoff);
        Serial.print("EVENT,heater_toggle,button,"); Serial.println(botao_aquecedor_onoff);
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
      Serial.println("ERR,COMMAND_TOO_LONG");
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


void requestMeasurementRange() {
    // Command to request the measurement range (example command, adjust as per documentation)
    byte requestRangeCommand[] = {0xFF, 0x01, 0x7D, 0x00, 0x00, 0x00, 0x00, 0x00, 0x82};

    mySerialCO2.write(requestRangeCommand, 9);
    delay(500); // Allow time for the sensor to respond

    // Read the response
    byte response[9];
    int index = 0;
    while (mySerialCO2.available() && index < 9) {
        response[index++] = mySerialCO2.read();
    }

    // Log all response bytes
    Serial.print("Response: ");
    for (int i = 0; i < index; i++) {
        Serial.print(response[i], HEX);
        Serial.print(" ");
    }
    Serial.println();

    // Parse the response to determine the range
    if (index == 9 && response[0] == 0xFF && response[1] == 0x7D) {
        int range = (response[2] << 8) | response[3]; // Combine two bytes for range
        Serial.print("Range: ");
        Serial.println(range);
    } else {
        Serial.println("Failed to read measurement range");
    }
}

void setMeasurementRange100000() {
    // Command to set the measurement range to 100000 ppm
    // The command bytes here are hypothetical and need to be adjusted based on the sensor's documentation
    byte setRange100000[] = {0xFF, 0x01, 0x99, 0x00, 0x86, 0xA0, 0x00, 0x00, 0x00};

    // Calculate the checksum
    setRange100000[8] = calculateChecksum(setRange100000);

    mySerialCO2.write(setRange100000, 9);
    delay(100); // Allow some time for sensor to process

    // Read response (if any)
    while (mySerialCO2.available()) {
        byte response = mySerialCO2.read();
        Serial.print(response, HEX);
        Serial.print(" ");
    }
    Serial.println();
}

byte calculateChecksum(byte packet[]) {
    byte checksum = 0xFF;
    for (int i = 1; i < 8; i++) {
        checksum -= packet[i];
    }
    return checksum;
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
