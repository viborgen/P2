// Biblioteker
#include <LiquidCrystal_I2C.h>
#include <Wire.h>

LiquidCrystal_I2C lcd(0x27);

float hastighed;

//piezoelementer
int aktivPiezo = 0;
float time1;
float time2;
int piezonummer = 1;

//tachometer
unsigned long timer;
unsigned long offset;
float omdrejningMotor = 0;
float omdrejningHjul = 0;

void setup() {
    Serial.begin(9600);

    //piezoelementer
    pinMode(A0, INPUT);
    pinMode(A3, INPUT);

    // LCD-setup
    lcd.begin(16, 2);
}

// Funktion, der printer alarmeringen på LCD-skærmen
void skaerm(int piezonummer, float hastighed) {
    if (hastighed <= 2.5) {  // Den printer dette, hvis køretøjet ikke kører for hurtigt
        lcd.clear();
        lcd.home();
        lcd.print("God dag :-)");
        lcd.setCursor(16, 0);
        lcd.print(piezonummer);  // For at sikre, at hastigheden følger med til det korrekte piezoelement
        lcd.setCursor(0, 1);
        lcd.print("Hastighed:");
        lcd.print(hastighed);
    } else {  // Dette printer den, hvis køretøjet kører for hurtigt
        lcd.clear();
        lcd.home();
        lcd.print("For hurtigt!!");
        lcd.setCursor(16, 0);
        lcd.print(piezonummer);  // For at sikre, at hastigheden følger med til det korrekte piezoelement
        lcd.setCursor(0, 1);
        lcd.print("Hastighed:");
        lcd.print(hastighed);
    }
}

//Funktion der beregner hastighed ud fra to tider
float hastighedfunc(float tid2, float tid1) {
    float tidtaget = (tid2 - tid1) / 1000;  //Tiden der er gået i sekunder
    float afstand = 0.43;                   //predefineret afstand i meter
    float hastighed = afstand / tidtaget;   //Beregner hastighed i m/s
    float hastighedkm = hastighed * 3.6;    //Omregner til km/t
    return hastighedkm;
}

void loop() {
    //Første piezo
    if (analogRead(A0) > 500 && aktivPiezo == 0) {  //Venter på at første piezo aktiveres
        time1 = millis();                           //noterer tiden
        piezonummer = 1;
        Serial.print(piezonummer);
        Serial.print(" ");
        Serial.println(0);       //printer data til Serial Monitor, der læses af Raspberry Pi i Python koden.
        skaerm(piezonummer, 0);  //Printer til skærm
        aktivPiezo = 1;
    }

    //Anden piezo
    if (analogRead(A3) > 500 && aktivPiezo == 1) {  //Venter på at første piezo har været aktiveret, og der modtages signal fra piezo 2.
        time2 = millis();                           //noter tiden ved piezo 2
        piezonummer = 2;
        hastighed = hastighedfunc(time2, time1);  //Udregner hastigheden der har været mellem de to piezoelementer ud fra en given afstand
        Serial.print(piezonummer);
        Serial.print(" ");
        Serial.println(hastighed);       //Printer data der læses af Raspberry Pi i python koden.
        skaerm(piezonummer, hastighed);  //Printer til skærm
        aktivPiezo = 2;
        offset = millis();
    }

    //Tachometer
    if (aktivPiezo == 2) {
        float tid1 = millis();
        piezonummer = 50;
        timer = millis() - offset;
        float irsensor = analogRead(A1);            //Læser fra IR-sensor
        if (irsensor < 20) {                        //Aktiveres når der læses en værdi under 20, hvilket er hvid.
            omdrejningHjul = omdrejningHjul + 0.5;  //Lægger en halv omgang til hver gang der læses hvid
            while (irsensor < 500) {                //For at IR-sensoren ikke læser samme værdi to gange, venter den her indtil der igen læses en værdi over 500.
                irsensor = analogRead(A1);
                float tid2 = millis();
                if (tid2 - tid1 > 400) {  //Hvis motoren stopper med en hvid streg foran ir-sensoren, afsluttes denne efter 0,4 sekunder.
                    break;
                }
            }
        }
        if (timer >= 1000) {                         //Alle de omdrejninger der måles indenfor et sekund
            aktivPiezo = 0;                          //Sættes til 0, så programmet kan starte forfra.
            omdrejningMotor = omdrejningHjul * 5.6;  //ganges med forholdet mellem det store og lille tandhjul for at få motorens rotationer.
            if (omdrejningMotor > 10) {              //Er der lavet mere end 10 omdrejninger
                Serial.print(piezonummer);           //Der printes piezonummer 50 for at signalere til Python koden at det er tachometrets data der kommer
                Serial.print(" ");
                Serial.println(omdrejningMotor);  //motorens omdrejninger til Python koden.
                omdrejningHjul = 0;               //Reset
            }
        }
    }
}
