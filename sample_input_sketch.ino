
/*
  Sample sketch for seding analog values into servo_in.py
  Used for recording servo movements in real time

  This sketch uses 2 potentiometers to both move control the servos and
  simultaneously send all values through serial.
*/


//#include <Servo.h>
#include <Adafruit_PWMServoDriver.h>
#include <Wire.h>

// PCA9685 to control servos
Adafruit_PWMServoDriver servo_driver = Adafruit_PWMServoDriver();

/////////////////////////
// This section sets up the potentiometers

// Set pin numbers
const int pot0 = A0;
const int pot1 = A1;

// Array of potentiometers, used to iterate over
int POTS[] = {pot0, pot1};
byte NUM_SERVOS = sizeof(POTS) / sizeof(int);

// Array of names, REQUIRED to set tab names/titles in the main app
const String NAMES[] = {"pot0", "pot1"};

//////////////////////////


// Variables for PCA9685 pulse length
const int SERVOMIN = 150;
const int SERVOMAX = 525;

// Wheter or not to send values over serial
boolean RECORD_FLAG = false;

long prev_write;
const int delay_time = 500;


// Move the servos and if necessary, send values over serial
void moveServos()
{
  int angle;
  String all_values = "";
  
  for (int i=0; i<NUM_SERVOS; i++)
  {
    int pot_value = analogRead(POTS[i]);
    int value = map(pot_value, 0, 1023, SERVOMIN, SERVOMAX);
    int angle = map(pot_value, 0, 1023, 0, 179);
    
    servo_driver.setPin(i, value);
    all_values = all_values + "," + angle;
  }
  
  // Send values over serial at appropriate interval, if recording
  if (RECORD_FLAG == true)
  {
    if ((millis() - prev_write) > delay_time)
    {
      Serial.println(all_values);
      prev_write = millis();
    }
  }
}
                                                                                                                                                                 

// Verify whether servo_in.py has sent a command
void checkForChar()
{
  // Read serial port for 'record' and 'stop' signals
  
  if (Serial.available() > 0)
  {
    char character = Serial.read();
    
    switch (character)
    {
      case 'r':  // Start 'recording', sending values over serial
        RECORD_FLAG = true;
        break;
        
      case 's':  // Stop sending values
        RECORD_FLAG = false;
        break;
        
      case 'n':  // Send names and number of servos to python
        for (byte i=0; i<NUM_SERVOS; i++)
        {
          Serial.print(NAMES[i]);
          Serial.print(',');
        }
        Serial.println();
        break;
        
    }
  }
}


void setup()
{
  Serial.begin(9600);
  
  servo_driver.begin();
  servo_driver.setPWMFreq(50);  // Analog servos run at ~60 Hz updates
}

void loop()
{
  moveServos();
  checkForChar();   
}
