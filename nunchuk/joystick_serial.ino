/*

  By: Daniyal Ansari

  About:
  
  This code is for controling the DSTR robot using the Wii Nunhchuk joystick, buttons, and accelerometers.

  Wires:
    
    White ----- GND
    Red ------- 5V
    Green ----- A4
    Yellow ---- A5

  MATH:

  Raw Values:

    int joy_x_axis = nunchuck_buf[0];
    int joy_y_axis = nunchuck_buf[1];

  Without 255 Inversion:

    int joy_x_axis = abs(2.55 * (nunchuck_buf[0]) - 331.5);
    int joy_y_axis = abs(2.55 * (nunchuck_buf[1]) - 331.5);

  With 255 Inversion:

    int joy_x_axis = 255 - (abs(2.55 * (nunchuck_buf[0]) - 331.5));
    int joy_y_axis = 255 - (abs(2.55 * (nunchuck_buf[1]) - 331.5));

*/

#include <Wire.h>
#include <math.h>

#define LED3_RED 2
#define LED2_RED 3
#define LED1_RED 4

#define LED3_GREEN 5
#define LED2_GREEN 6
#define LED1_GREEN 7

#define LED3_BLUE 8
#define LED2_BLUE 9
#define LED1_BLUE 10

static uint8_t nunchuck_buf[6];   // array to store nunchuck data,
static uint8_t nunchuck_data[4];

float a = 0;
float throttle = 0;

float angle = 0;

int allowSerialWrite = 0;
int armMode = 0; // 0 = Off, 1 = On
int yServoSelect = 2; // 2-5, Corresponds to servo channels on BeagleBone Blue.

int grabberState = 0; // 0 = Open, 1 = Close, Is grabber open or closed?

int c_buttonState = 1;
int c_buttonStatePrevious = 1;
int c_buttonPushCounter;

int z_buttonState = 0;
int z_buttonStatePrevious = 0;
int z_buttonPushCounter;

void setup() {
  Serial.begin(38400);
  
  pinMode(LED3_RED, OUTPUT);
  pinMode(LED2_RED, OUTPUT);
  pinMode(LED1_RED, OUTPUT);

  pinMode(LED3_GREEN, OUTPUT);
  pinMode(LED2_GREEN, OUTPUT);
  pinMode(LED1_GREEN, OUTPUT);

  pinMode(LED3_BLUE, OUTPUT);
  pinMode(LED2_BLUE, OUTPUT);
  pinMode(LED1_BLUE, OUTPUT);

  nunchuck_setpowerpins(); // use analog pins 2&3 as fake gnd & pwr
  nunchuck_init(); // send the initilization handshake
}

void loop() {

//  digitalWrite(LED, HIGH);
  nunchuck_get_data();

  // map nunchuk data to a servo data point
  int x_axis = map(nunchuck_buf[0], 23, 222, 180, 0);
  int y_axis = map(nunchuck_buf[1], 32, 231, 0, 180);

  nunchuck_print_data();

}

static void nunchuck_setpowerpins() {
#define pwrpin PORTC3
#define gndpin PORTC2
  DDRC |= _BV(pwrpin) | _BV(gndpin);
  PORTC &= ~ _BV(gndpin);
  PORTC |=  _BV(pwrpin);
  delay(100);  // wait for things to stabilize
}

// initialize the I2C system, join the I2C bus,
// and tell the nunchuck we're talking to it
void nunchuck_init() {
  Wire.begin();                      // join i2c bus as master
  Wire.beginTransmission(0x52);     // transmit to device 0x52
  Wire.write(0x40);            // sends memory address
  Wire.write(0x00);            // sends sent a zero.
  Wire.endTransmission();     // stop transmitting
}

// Send a request for data to the nunchuck
// was "send_zero()"
void nunchuck_send_request() {
  Wire.beginTransmission(0x52);     // transmit to device 0x52
  Wire.write(0x00);            // sends one byte
  Wire.endTransmission();     // stop transmitting
}

// Receive data back from the nunchuck,
int nunchuck_get_data()
{
    int cnt=0;
    Wire.requestFrom (0x52, 6);     // request data from nunchuck
    while (Wire.available ()) {
      // receive byte as an integer
      nunchuck_buf[cnt] = nunchuk_decode_byte(Wire.read());
      cnt++;
    }
    nunchuck_send_request();  // send request for next data payload
    // If we recieved the 6 bytes, then go print them
    if (cnt >= 5) {
     return 1;   // success
    }
    return 0; //failure
}

// Print the input data we have recieved
// accel data is 10 bits long
// so we read 8 bits, then we have to add
// on the last 2 bits.  That is why I
// multiply them by 2 * 2

void nunchuck_print_data() {
  
  int accel_x_axis = nunchuck_buf[2]; // * 2 * 2; 
  int accel_y_axis = nunchuck_buf[3]; // * 2 * 2;
  int accel_z_axis = nunchuck_buf[4]; // * 2 * 2;
  
  int z_button = 1;
  int c_button = 1;

  // byte nunchuck_buf[5] contains bits for z and c buttons
  // it also contains the least significant bits for the accelerometer data
  // so we have to check each bit of byte outbuf[5]

  if ((nunchuck_buf[5] >> 0) & 1)
    z_button = 0;
  if ((nunchuck_buf[5] >> 1) & 1)
    c_button = 0;

    c_buttonState = c_button;
    if (c_buttonState != c_buttonStatePrevious)
    {
      if (c_buttonState == 1){
        c_buttonPushCounter++;
      }
      c_buttonStatePrevious = c_buttonState;
    }
    
    if (c_buttonPushCounter % 3 == 0){
      
    }

    z_buttonState = z_button;
    if (z_buttonState != z_buttonStatePrevious)
    {
      if (z_buttonState == 1){
        z_buttonPushCounter++;
      }
      z_buttonStatePrevious = z_buttonState;
    }
    
    if (z_buttonPushCounter % 3 == 0){
      
    }

  if (c_buttonPushCounter > 3){
    c_buttonPushCounter = 1;
    }

  if (z_buttonPushCounter > 2){
    z_buttonPushCounter = 1;
    }

  if ((nunchuck_buf[5] >> 2) & 1) 
    accel_x_axis += 2;
  if ((nunchuck_buf[5] >> 3) & 1)
    accel_x_axis += 1;

  if ((nunchuck_buf[5] >> 4) & 1)
    accel_y_axis += 2;
  if ((nunchuck_buf[5] >> 5) & 1)
    accel_y_axis += 1;

  if ((nunchuck_buf[5] >> 6) & 1)
    accel_z_axis += 2;
  if ((nunchuck_buf[5] >> 7) & 1)
    accel_z_axis += 1;

  //For finding Angle

  float joy_x_angle = abs(2.55 * (nunchuck_buf[0]) - 331.5);
  float joy_y_angle = abs(2.55 * (nunchuck_buf[1]) - 331.5);

  int angle = abs((atan(joy_y_angle / joy_x_angle) * 4068) / 71);

  if ( ( joy_x_angle < 6 && joy_x_angle > -6 ) && ( joy_y_angle < 6 && joy_y_angle > -6 ) ) {
    int angle = 254;
  }

  if (angle < 45){
    angle = 5.6666666666667 * (angle);
    if (angle <= 11){
      angle = 0;
    }
    else{
    }
  }
  
  else if (angle >= 45){
    angle = -5.6666666666667 * (angle) + 510;
    if (angle <= 11){
      angle = 0;
    }
    else{
    }
  }



















  
  
  // For finding Direction

  int joy_x_axis_direction = 2.55 * (nunchuck_buf[0]) - 331.5;
  int joy_y_axis_direction = 2.55 * (nunchuck_buf[1]) - 331.5;

//  int joy_x_axis_direction = nunchuck_buf[0];
//  int joy_y_axis_direction = nunchuck_buf[1];



//  int joy_x_axis_throttle = 255 - (abs(0.9844559585 * (nunchuck_buf[0]) - 3.419689119));
//  int joy_y_axis_throttle = 255 - (abs(0.9844559585 * (nunchuck_buf[1]) - 3.419689119));

  int joy_x_axis_throttle = 255 - abs(map(nunchuck_buf[0], 27, 220, -255, 255)); //map(value, fromLow, fromHigh, toLow, toHigh)
  int joy_y_axis_throttle = 255 - abs(map(nunchuck_buf[1], 30, 220, -255, 255));     //map(value, fromLow, fromHigh, toLow, toHigh)

  if(joy_x_axis_throttle > 230){

    joy_x_axis_throttle = 254;
    
    }

    else{

      joy_x_axis_throttle = abs(joy_x_axis_throttle);  
      
    }

    if(joy_y_axis_throttle > 240){

    joy_y_axis_throttle = 254;
    
    }

    else{
      joy_y_axis_throttle = abs(joy_y_axis_throttle);  
    }



    


//  int joy_x_axis_throttle = nunchuck_buf[0];
//  int joy_y_axis_throttle = nunchuck_buf[1];



//  Serial.write(joy_x_axis_throttle);
//  Serial.write(",");
//  Serial.writeln(joy_y_axis_throttle);



















  
  int throttle = 255 - ( sqrt( sq ( 255 - joy_x_axis_throttle ) + sq ( 255 - joy_y_axis_throttle ) ) );

//Serial.print(joy_x_axis_direction);
//Serial.print(",");
//Serial.println(joy_y_axis_direction);

if (c_buttonPushCounter == 1){

   digitalWrite(LED1_BLUE,HIGH);
   digitalWrite(LED2_GREEN,LOW);
   digitalWrite(LED3_GREEN,LOW);
  
  }

else if (c_buttonPushCounter == 2){

   digitalWrite(LED1_BLUE,LOW);
   digitalWrite(LED2_GREEN,HIGH);
   digitalWrite(LED3_GREEN,LOW);
    
  }

else if (c_buttonPushCounter == 3){
   
   digitalWrite(LED1_BLUE,LOW);
   digitalWrite(LED2_GREEN,LOW);
   digitalWrite(LED3_GREEN,HIGH);
    
  }

if (allowSerialWrite >= 50){ //Limits the number of packets sent over serial

//  if ( ( joy_x_axis_direction > -25 && joy_x_axis_direction < 5 ) && ( joy_y_axis_direction > -20 && joy_y_axis_direction < -2 ) ) {
    
  if ( ( joy_x_axis_direction > -30 && joy_x_axis_direction < 5 ) && ( joy_y_axis_direction > -20 && joy_y_axis_direction < -2 ) ) {


//    Serial.print(187);Serial.print(",");
//    Serial.print(254);Serial.print(",");
//    Serial.print(187);Serial.print(",");
//    Serial.println(254);

    Serial.write(187);
    Serial.write(254);
    Serial.write(187);
    Serial.write(254);
    
    Serial.write(accel_x_axis);
    Serial.write(accel_y_axis);
    Serial.write(accel_z_axis);
    
    Serial.write(c_buttonPushCounter);
    Serial.write(z_buttonPushCounter);
    
    Serial.write(grabberState);
    Serial.write(armMode);
    Serial.write(yServoSelect);

  }

  else if (joy_y_axis_direction > abs(joy_x_axis_direction)) {

    if (joy_x_axis_direction < 0) {
    
      Serial.write(170);
      Serial.write(throttle);
      Serial.write(170);
      Serial.write(angle);

      Serial.write(accel_x_axis);
      Serial.write(accel_y_axis);
      Serial.write(accel_z_axis);
      
      Serial.write(c_buttonPushCounter);
      Serial.write(z_buttonPushCounter);
      
      Serial.write(grabberState);
      Serial.write(armMode);
      Serial.write(yServoSelect);
    
    }

    else if (joy_x_axis_direction > 0) {
    
      Serial.write(170);
      Serial.write(angle);
      Serial.write(170);
      Serial.write(throttle);

      Serial.write(accel_x_axis);
      Serial.write(accel_y_axis);
      Serial.write(accel_z_axis);
      
      Serial.write(c_buttonPushCounter);
      Serial.write(z_buttonPushCounter);
      
      Serial.write(grabberState);
      Serial.write(armMode);
      Serial.write(yServoSelect);
    
    }
    
  }

  else if (joy_y_axis_direction < (-1) * abs(joy_x_axis_direction)) {

    if (joy_x_axis_direction < 0) {
    
      Serial.write(187);
      Serial.write(throttle);
      Serial.write(187);
      Serial.write(angle);

      Serial.write(accel_x_axis);
      Serial.write(accel_y_axis);
      Serial.write(accel_z_axis);
      
      Serial.write(c_buttonPushCounter);
      Serial.write(z_buttonPushCounter);
      
      Serial.write(grabberState);
      Serial.write(armMode);
      Serial.write(yServoSelect);
    
    }
    
    else if (joy_x_axis_direction > 0) {
    
      Serial.write(187);
      Serial.write(angle);
      Serial.write(187);
      Serial.write(throttle);
      
      Serial.write(accel_x_axis);
      Serial.write(accel_y_axis);
      Serial.write(accel_z_axis);
      
      Serial.write(c_buttonPushCounter);
      Serial.write(z_buttonPushCounter);
      
      Serial.write(grabberState);
      Serial.write(armMode);
      Serial.write(yServoSelect);
    
    }

  }

  else if (joy_x_axis_direction > 0) {
    
    Serial.write(170);
    Serial.write(throttle);
    Serial.write(187);
    Serial.write(angle);
    
    Serial.write(accel_x_axis);
    Serial.write(accel_y_axis);
    Serial.write(accel_z_axis);
    
    Serial.write(c_buttonPushCounter);
    Serial.write(z_buttonPushCounter);
    
    Serial.write(grabberState);
    Serial.write(armMode);
    Serial.write(yServoSelect);
  
  }

  else if (joy_x_axis_direction < 0) {
  
    Serial.write(187);
    Serial.write(angle);
    Serial.write(170);
    Serial.write(throttle);
    
    Serial.write(accel_x_axis);
    Serial.write(accel_y_axis);
    Serial.write(accel_z_axis);
    
    Serial.write(c_buttonPushCounter);
    Serial.write(z_buttonPushCounter);
    
    Serial.write(grabberState);
    Serial.write(armMode);
    Serial.write(yServoSelect);
  
  }

  allowSerialWrite = 0;

}

allowSerialWrite++;  

}

// Encode data to format that most wiimote drivers except
// only needed if you use one of the regular wiimote drivers
char nunchuk_decode_byte (char x) {
  x = (x ^ 0x17) + 0x17;
  return x;
}
