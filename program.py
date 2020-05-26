import threading    # Bibliotek til at køre flere programmer sideløbende
import queue        # Bibliotek til at kunne tilgå variabler fra threads
import time         # Bibliotek til at tilgå tid

# Importer andre filer
from nummerplade import nummerpladegenkendelse
from motorv2 import *
from readArduino import *

starttid = time.time()
sluttid = starttid
firstPiezo = True
my_queue = queue.Queue() # Indsættes i nummerpladegenkendelse for at kunne aflæse værdier fra en thread

nummerpladeGenkendt = False
pieozo1gennemkoert = False

# Funktion for at kunne køre samme threads flere gange
def threadhack(navn):
    navn = threading.Thread(target=nummerpladegenkendelse, args=(1,0,my_queue,)) # target er funktionen, der skal køres i den thread, args er argumenterne til target
    return navn
threadnummer = 1

while True: # Main loop
    arduinoData = readArduino()             # Funktion til at læse data fra piezoelementer gennem Arduino
    print(arduinoData[0], arduinoData[1])   # 0 er piezonummer, 1 er hastigheden
    if arduinoData[0] == 1 and arduinoData[1] == 0 and not threadhack(threadnummer).is_alive(): # Hvis bilen er ved det første piezoelement
        threadhack(threadnummer).start()    # Kør biltypesensor-program
        firstPiezo = False                  # Nu er vi forbi det første piezoelement
        pieozo1gennemkoert = True           # Nu er vi forbi det første piezoelement
    elif not my_queue.empty() and pieozo1gennemkoert == True: # Hvis biltypesensor-programmet har returneret noget
        pieozo1gennemkoert = False
        nummerpladeGenkendt = my_queue.get()# Få boolean om, hvorvidt køretøj er udrykning eller ej
    elif nummerpladeGenkendt == True:       # Hvis det er et udrykningskøretøj
        print("Udrykningskøretøj. Fiktivt bump skal sættes til startposition.")
    
    motorControl(arduinoData, 255, 255)     # Funktionen til at køre motoren
    time.sleep(0.5)                         # Lille delay, så koden ikke bare begynder forfra med det samme

    originalPos = 0                         # Værdi til tracking af motoren

    threadnummer = threadnummer + 1         # Navnet ændres, så threaden kan køres igen
    firstPiezo = True                       # Boolean, så koden venter på en ny bil