int pinR = 10;
//if RGB LED:
int pinG = 11;
int pinB = 12;

int pinUV = 8;
int LDR = A0;
int msg;
int signal;
//if DHT temperature sensor
#include "DHT.h"
#define DHTPIN A1
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin (9600);
  pinMode(pinR, OUTPUT);
  //if RGB LED:
  pinMode(pinG, OUTPUT);
  pinMode(pinB, OUTPUT);

  pinMode(pinUV, OUTPUT);
  pinMode(LDR, INPUT);

  digitalWrite(pinR, LOW); 
  digitalWrite(pinG, LOW); 
  digitalWrite(pinB, LOW); 
  digitalWrite(pinUV, LOW); 
  //if DTH temperature sesor:
  dht.begin();
}

void loop() {

  if (Serial.available() > 0) {
    msg = Serial.read();
  signal = msg - 48; //ASCII (0) = 48
  if (signal == 0){
    digitalWrite(pinR, HIGH); 
  }
  if (signal == 1){
    digitalWrite(pinR, LOW); 
  }
  //if RGB LED
  if (signal == 2){
    digitalWrite(pinG, HIGH); 
  }
  if (signal == 3){
    digitalWrite(pinG, LOW); 
  }
  if (signal == 4){
    digitalWrite(pinB, HIGH); 
  }
  if (signal == 5){
    digitalWrite(pinB, LOW); 
  }

  
  if (signal == 6){
    digitalWrite(pinUV, HIGH); 
  }
  if (signal == 7){
    digitalWrite(pinUV, LOW); 
  }
  if (signal == 8) {
    Serial.println(String(analogRead(LDR)));
  }
  //if DHT temperatur sensor
  if (signal == 9){
    Serial.println(String(dht.readTemperature()));
  }}
}
