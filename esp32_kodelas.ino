#include <analogWrite.h>          // importerer analog funksjoner

const int VRx = 4;                // pinne for å styre joystick i x-retning
const int VRy = 2;                // pinne for å styre joystick i y-retning
const int SW = 15;                // pinne for switch, aka trykk knapp
const int RingKlokkKnapp = 5;     // pinne for ringe klokke knappen
//const int ring_klokk = ;        // pinne for buzzer

const int NoAccesLed = 23;        // led som lyser når du ikke får tilgang til boligen
const int DoorOpenLed = 22;       // led som lyser når døren åpnes
const int RingKlokkLed = 21;      // led som lyser når du holder inne ringe klokka  

long buttonDelay = 250;           // delay for noen knapper
const int timeToPinReset = 5000;  // reset time for pinkoden

int thePinCode [4] = {2,1,4,3};   // pinkode


void setup() {
  //input modus for input pinner
  pinMode(VRx,INPUT);                 
  pinMode(VRy,INPUT);                 
  pinMode(SW,INPUT_PULLUP);           
  pinMode(RingKlokkKnapp, INPUT);   

  //input modus for output pinner
  //pinMode(RingKlokk, OUTPUT);      
  pinMode(NoAccesLed, OUTPUT);
  pinMode(DoorOpenLed, OUTPUT);
  pinMode(RingKlokkLed, OUTPUT);
  Serial.begin(115200);
}

void doorLock(){
  int input = 0;                // input signal avhengig av hvilken retning joysticken styres
  int temp = 0;                 // variabel som skal matche input 
  int index = 0;                // index som input verdiene settes
  int aPinCodeAttempt[4] = {};  // array for pinkode forsøk
  bool feilPin = false;         // 

  unsigned long previousMillis = millis();      // henter current millis()
  unsigned long currentMillis = previousMillis; // setter currentMillis() lik previousMillis()

 while(true){
  int enter = digitalRead(SW);     // enter knapp
  int y = analogRead(VRy);         // y retning
  int x = analogRead(VRx);         // x retning

  digitalWrite(RingKlokkLed, LOW);    // resetter ringe klokke leden når knappen for den ikke holdes inne
  //digitalWrite(RingKlokk, LOW);

    if((analogRead(VRx) == 0) || (analogRead(VRx) == 4095) || (analogRead(VRy) == 0) || (analogRead(VRy) == 4095) || (digitalRead(SW) == 0)){
      previousMillis = currentMillis;                      
      // hvis joystick brukes starter idle_time på nytt
    }
    currentMillis = millis();
    
    // Hvis joysticken ikke har vært rørt på 5 sekunder resettes pinkode forsøke til 0-stilling, samt alle andre variabler
    if(currentMillis - previousMillis > timeToPinReset){
      Serial.println("Resetter PinCodeAttempt~~");
      previousMillis = currentMillis;      
      input = 0;
      temp = 0;
      index = 0;
      aPinCodeAttempt[0] = 0;
      aPinCodeAttempt[1] = 0;
      aPinCodeAttempt[2] = 0;
      aPinCodeAttempt[3] = 0;
    }

  // velger input verdier avhengig av retning til joysticken
  if (x == 0){
    input = 1;
    delay(buttonDelay);
    }
  else if (x == 4095){
    input = 2;
    delay(buttonDelay);
    }
  else if (y == 0){
    input = 3;
    delay(buttonDelay);
    }
  else if (y == 4095){
    input = 4;
    delay(buttonDelay);
    }
  else if (enter == 0){
    input = 5;
    delay(buttonDelay);
    }

  // Når input verdien ikke er lik temp eller 5 så legges input i pinkode forsøke sitt array
  if ((input != temp) && (input != 5)){
    temp = input;                         // setter temp = input slik at det samme signalet ikke blir lagt inn tusenvis av ganger i løpet av sekundet
    aPinCodeAttempt[index] = input;
    Serial.print(index);
    Serial.print("-");
    Serial.println(input);
    index = index + 1;
    if(index >= 4){                       // hvis du prøver å legge inn flere siffer enn størrelsen til arrayet så starter du pånytt
      index = 0;     
      }
  } 

  // Når du trykker enter
  if(input == 5){
    // variabler resettes
    index = 0;
    input = 0;
    temp = 0;
    
    // sjekker om alle indexene til aPinCodeAttempt matcher pinCode
    for(int i=0; i<4; i++){
      if (aPinCodeAttempt[i] != thePinCode[i]){
        feilPin = true;                   // Hvis ikke alle matcher setter feilPin til true
      }
    }      

    if (!feilPin){                        // hvis alle indeksene er riktig åpnes døren, og et led lyser for å indikere dette.
      Serial.println("Døren er åpnet"); 
      // resetter aPinCodeAttempt til neste forsøk
      aPinCodeAttempt[0] = 0;
      aPinCodeAttempt[1] = 0;
      aPinCodeAttempt[2] = 0;
      aPinCodeAttempt[3] = 0;
      digitalWrite(DoorOpenLed, HIGH);
      delay(1000);
      digitalWrite(DoorOpenLed, LOW);
    }

    else if (feilPin){                      // hvis feilPin er satt til true får du beskjed om å prøve igjen, og et led lyser for å indikere dette
      Serial.println("Prøv igjen"); 
      // resetter aPinCodeAttempt til neste forsøk
      aPinCodeAttempt[0] = 0;
      aPinCodeAttempt[1] = 0;
      aPinCodeAttempt[2] = 0;
      aPinCodeAttempt[3] = 0;
      feilPin = false;
      digitalWrite(NoAccesLed, HIGH);
      delay(1000);
      digitalWrite(NoAccesLed, LOW);
     }
    }
    
    // ringeklokke som går når en knapp holdes inne
    while(digitalRead(RingKlokkKnapp)){
      //digitalWrite(RingKlokk, HIGH);
      digitalWrite(RingKlokkLed, HIGH);
      break;
    }
    // får signaler fra mqtt om døren åpnes eller ikke
    // if (mqtt.read(open_door) == 1){
    //   Serial.println("Døren er åpen");
    //   digitalWrite(DoorOpenLed, HIGH);
    //   delay(1000);
    //   digitalWrite(DoorOpenLed, LOW);
    // }

    // if (mqtt.read(open_door) == 2){
    //   Serial.println("Ingen adgang");
    //   digitalWrite(NoAccesLed, HIGH);
    //   delay(1000);
    //   digitalWrite(NoAccesLed, LOW);
    // }

 }
}

void loop() {
  doorLock();
}
