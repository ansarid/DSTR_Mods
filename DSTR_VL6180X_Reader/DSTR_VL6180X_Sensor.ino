#include <Wire.h>

#include <SparkFun_VL6180X.h>

#define VL6180X_ADDRESS 0x29

VL6180x sensor(VL6180X_ADDRESS);

void setup() {

  Serial.begin(115200); //Start Serial at 115200bps
  Wire.begin(); //Start I2C library
  delay(100); // delay .1s
  sensor.VL6180xInit() != 0;

  sensor.VL6180xDefautSettings(); //Load default settings to get started.
  
  delay(1000); // delay 1s

}

void loop() {

  //Get Distance and report in mm
  Serial.println(sensor.getDistance()); 

  delay(100);  
};
