# Importering af biblioteker
import requests
import time
from pprint import pprint 

#understående bruges til at finde det seneste billede
import glob
import os

# For at kunne tilgå variabler fra threads
import queue

udrykning = False

# Funktion til at genkende biltypen
def nummerpladegenkendelse(kamera , lokalt, out_queue):             #out_queue er til for at kunne tilgå variabler fra denne som thread.
    print("nummerplade kører")
    if kamera == 1:                                                 # Hvis brug af kamera er valgt
        os.system('fswebcam -r 640x480 --no-banner billeder/%Y-%m-%d_%H%M%S.jpg') #tag billede
    
    #Undersøger den seneste fil fra billede-mappen
    list_of_files = glob.glob('billeder/*')                         #find alle filer i mappen
    seneste = max(list_of_files, key=os.path.getctime)              #find den seneste fil. Dette ved brug af max og key=os.path.getctime
    #Læs nummerplade fra billede. Stor del er taget fra Platerecognizer
    regions = ['dk']                                                #Der skal vælges region
    #Der skal afgøres om der testes lokalt eller online
    if lokalt == 1:                                                 # Hvis der testes lokalt
        with open(seneste, 'rb') as fp:                             #billedet åbnes her
            response = requests.post(
            'http://localhost:8080/alpr',                           #til lokalt brug
            data=dict(regions=regions),
            files=dict(upload=fp),
            headers={'Authorization': 'Token <API_KODE>'})          #Vores API kode skal indsættes, er undladet for en sikkerheds skyld
    else:
        with open(seneste, 'rb') as fp:                             #billedet åbnes her
            response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',     #tager brug af online API
            data=dict(regions=regions),
            files=dict(upload=fp),
            headers={'Authorization': 'Token <API_KODE>'})          #Vores API kode igen

    #Sortering af modtaget json data
    sorter = response.json()                                        #Denne er lavet for at kunne sortere deres resultater. Det eneste vi skal bruge er nummerpladen.
    nummerplade = sorter["results"][0]["plate"]                     #derfor sorteres denne fra her
    print("Nummerpladen er: "+nummerplade)                          #Nummerplade udskrives

    udrykningsregister = ["br481td", "000000", "aa00000", "jw22432","bk70286"] #Database over "udrykningskøretøjer"
    
    if(nummerplade in udrykningsregister):                          # Hvis numerpladen er i registret, er det et udrykningskøretøj
        udrykning = True
    else:
        udrykning = False
    print("Nummerplade i database: ", udrykning)
    out_queue.put(udrykning)                                        #udrykning "returneres"

