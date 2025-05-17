#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>
#include <Arduino.h>
#include <driver/i2s.h>
#include <BluetoothSerial.h>

// Gyro setup
Adafruit_MPU6050 mpu;
#define TOUCH_SENSOR_PIN 5  // Change pin as needed

// I2S Microphone config
#define SAMPLE_RATE 8000
#define BUFFER_SIZE 1024  // Smooth streaming

#define I2S_PORT I2S_NUM_0

#define BITS_PER_SAMPLE 16

#define I2S_BCLK 14
#define I2S_WS 15
#define I2S_DIN 32

BluetoothSerial SerialBT;
int16_t audioBuffer[BUFFER_SIZE];

float prevAccelX = 0, prevAccelY = 0;
unsigned long lastSwipeTime = 0;
float debounceTime = 300;
bool micEnabled = false;

void setup() {
    Serial.begin(115200);

    Serial.println("Initializing MPU6050...");
    if (!mpu.begin()) {
        Serial.println("Failed to find MPU6050 chip");
        while (1) delay(10);
    }
    Serial.println("MPU6050 Connected!");

    mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
    mpu.setGyroRange(MPU6050_RANGE_500_DEG);
    mpu.setFilterBandwidth(MPU6050_BAND_10_HZ);

    pinMode(TOUCH_SENSOR_PIN, INPUT);

    SerialBT.begin("ESP32_MIC");
    Serial.println("Bluetooth started. Pair with 'ESP32_MIC'.");

    initI2S();
    Serial.println("Setup Complete.\n");
}

void loop() {
    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    float accelX = (a.acceleration.x * 0.7) + (prevAccelX * 0.3);
    float accelY = (a.acceleration.y * 0.7) + (prevAccelY * 0.3);

    prevAccelX = accelX;
    prevAccelY = accelY;

    float swipeThreshold = 7.0;

    if (millis() - lastSwipeTime > debounceTime) {
        if (accelY > swipeThreshold) {
            Serial.println("⬆ Up Swipe Detected!");
            lastSwipeTime = millis();

            int touchState = digitalRead(TOUCH_SENSOR_PIN);
            if (touchState == HIGH) {
                Serial.println("Touch Detected! Microphone ON.");
                micEnabled = true;
            } else {
                Serial.println("Touch Not Detected. Microphone OFF.");
                micEnabled = false;
            }
        } else {
            // Any other gesture disables the mic
            //Serial.println("Other gesture detected. Microphone OFF.");
            micEnabled = false;
        }
    }

    // Handle microphone stream
    if (micEnabled && SerialBT.hasClient()) {
        size_t bytesRead = 0;
        esp_err_t result = i2s_read(I2S_PORT, audioBuffer, BUFFER_SIZE * sizeof(int16_t), &bytesRead, 100 / portTICK_PERIOD_MS);
        if (result == ESP_OK && bytesRead > 0) {
            SerialBT.write((uint8_t*)audioBuffer, bytesRead);
        } else {
            Serial.println("I2S read failed or no data.");
        }
    } else if (micEnabled && !SerialBT.hasClient()) {
        Serial.println("Waiting for Bluetooth connection...");
    }

    delay(100);
}

void initI2S() {
    i2s_config_t i2s_config = {
        .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX),
        .sample_rate = SAMPLE_RATE,
        .bits_per_sample = (i2s_bits_per_sample_t)BITS_PER_SAMPLE,
        .channel_format = I2S_CHANNEL_FMT_ONLY_LEFT,
        .communication_format = I2S_COMM_FORMAT_I2S,
        .intr_alloc_flags = 0,
        .dma_buf_count = 8,
        .dma_buf_len = BUFFER_SIZE,
        .use_apll = false,
        .tx_desc_auto_clear = false,
        .fixed_mclk = 0
    };

    i2s_pin_config_t pin_config = {
        .bck_io_num = I2S_BCLK,
        .ws_io_num = I2S_WS,
        .data_out_num = I2S_PIN_NO_CHANGE,
        .data_in_num = I2S_DIN
    };

    if (i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL) != ESP_OK) {
        Serial.println("Failed to install I2S driver");
        return;
    }

    if (i2s_set_pin(I2S_PORT, &pin_config) != ESP_OK) {
        Serial.println("Failed to set I2S pins");
        return;
    }

    Serial.println("I2S initialized successfully");
}