# Importering af biblioteker
import RPi.GPIO as GPIO
import time
import math

# Importering af anden fil
from readArduino import *

# Setup af pins på Raspberry Pi
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(11, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)

tachometer = 0 
motorMoved = False

# Funktion til at beregne motorens køretid ud fra antal rotationer og spænding
def calculateTeroreticalTime(voltage, rotations ):
    timeToTarget = (0.1190283929*rotations)/(voltage)
    print("tid til mål:", timeToTarget)
    return timeToTarget

# Funktion til at beslutte, hvor meget motoren skal rotere ud fra bilens hastighed
def calculateRotations(carSpeed):
    rotations = 0
    print(carSpeed)
    if (carSpeed <=5 and carSpeed >= 2.5):
        rotations = 11.25*carSpeed
        print("rotationer til position:" , rotations)
    if(carSpeed >5):
        rotations = 11.25*5
    return rotations


#Beregn spænding til motoren ud fra PWM
def calculateMotorVoltage(pvm):
    motorVoltage = (1.0023*0.047059*pvm)-1.6514
    print("bestemmer spænding over motor:", motorVoltage)
    return motorVoltage

#Beregner modellens rotationer ud fra tid og spænding
def calculateModelRotations(time, voltage):
    rotations = (57.78728173*voltage* time)/(2*math.pi)
    print("model rotationer", rotations)
    return rotations

# Funktion til at køre fremad
def forward():
    GPIO.output(13,GPIO.HIGH)
    GPIO.output(11, GPIO.LOW)

# Funktion til at køre beglæns
def reverse():
    GPIO.output(13,GPIO.LOW)
    GPIO.output(11, GPIO.HIGH)

# Funktion til at bremse
def motor_break():
    GPIO.output(11,GPIO.LOW)
    GPIO.output(13, GPIO.LOW)


#Bevæger motoren fremad eller bagud i et vis stykke tid
def DriveMotor(direction, duration):
    runtime = time.time()
    while (direction == 1 and duration >= time.time() - runtime ):
        forward()
    while (direction == 0 and duration >= time.time() - runtime):
        reverse()
    print("stopper motor")
    motor_break()
    
# Funktion, der styrer motorens bevægelse samt tilbagekobling
def motorControl (arduinoData, startPwm, regulatingPwm):
    motorMoved = False
    if arduinoData[0] == 2 and motorMoved == False:                 # Hvis bilen har kørt forbi det andet piezoelement
        carSpeed = arduinoData[1]                                   #hastigheden defineres fra Arduinoen
        global originalPos                                          #bruges til at holde styr på hvor mange omdrejninger motoren har taget.
        originalPos = calculateRotations(carSpeed)
        print("Regnet rotationer: ",originalPos)
        motorVoltage = calculateMotorVoltage(startPwm)
        motorDuration = calculateTeroreticalTime(motorVoltage,calculateRotations(carSpeed))
        DriveMotor(1, motorDuration)
        motorMoved = True
    elif arduinoData[0] == 50 and motorMoved == True:               #tachometret udsendes som værende 50. Hvis dette er tilfældet, aktiveres denne
        tachometer = arduinoData [1]                                #nu er arduinoData[1] tachometrets måling i stedet
        fejl = tachometer - calculateRotations(carSpeed)            #sammenligner tachometrets måling med den udregnede måling
        print("Tachometer: ",tachometer)
        print("Fejl:", fejl)
        driveTime = calculateTeroreticalTime(calculateMotorVoltage(regulatingPwm), fejl) #hvor længe den skal køre for at ændre fejlen.
        if (fejl > 0):                                              #afgør hvilken retning motoren skal bevæge sig
            DriveMotor(1,driveTime)
        else:
            DriveMotor(0,driveTime)
