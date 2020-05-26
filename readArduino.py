import serial 								# Bibliotek til at aflæse Arduinos serielle monitor

hastighed = 0
piezonummer = 0
ser = serial.Serial('/dev/ttyACM0',9600) 	# Porten med Arduinoen

def readArduino():
	a = ser.readline() 						#læser arduino serial

	# Disse to linjer fjerner unødig data
	b = a.decode()
	c = b.rstrip()

	d = c.split() 							#opsplitter en string ved hvert mellemrum

	# De to typer data fra d splittes op
	piezonummer = int(d[0])
	hastighed = float(d[1])

	return piezonummer, hastighed