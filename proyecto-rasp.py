import urllib.request
import urllib.parse
import json
import time
from serial import Serial
import threading

import gpiozero
import RPi.GPIO as gpio

# Sensores
ledPin = gpiozero.PWMLED(18)
servoPin = gpiozero.AngularServo(17, min_angle=-180, max_angle=180)
bz = gpiozero.Buzzer(16)
gpio.setmode(gpio.BCM)
gpio.setup(12, gpio.OUT)


# Serial
ser = Serial('/dev/ttyACM0',9600)
s = [0]

params = {
        "id":1,        
        "temperatura": 28.01,
        "humedad": "18%",
        "luminosidad": 100,
        "movimiento": False,
        "humo": "0%",
        "flama": False
    }

# Variables de actuadores
actuadorLuz = [ledPin]
actuadorPuerta = [servoPin]
actuadorVentilador = [1]
actuadorAspersor = [1]
actuadorAlarma = [bz]

# Petición a el servidor
def peticion():
    url = "http://192.168.43.76:4000/datos"  
    #url = "http://192.168.1.145:4000/datos"
    data = json.dumps(params).encode('utf8')
    request = urllib.request.Request(url,data=data,headers={'content-type': 'application/json'})
    with urllib.request.urlopen( request) as response:         
        response_text = response.read()         
        #print( response_text )
        cambiarValores(json.loads(response_text))


# función que actualiza valores de actuadores
def cambiarValores(valores):
    luces(valores["luz"])
    puerta(valores["puerta"])
    ventilador(valores["ventilador"])
    aspersor(valores["aspersor"])
    alarma(valores["alarma"])

def luces(val):
    if val:
        # prendemos cada luz
        for luz in actuadorLuz:
            # TODO: prender luces 
            luz.value = 1
            pass
    else:
        # Apagamos cada luz
        for luz in actuadorLuz:
            # TODO: Apagar luces
            luz.value = 0
            pass

def puerta(val):
    if val:
        # Abrir puerta
        for p in actuadorPuerta:
            # TODO: Abrir puerta
            p.angle = -180
            pass
    else:
        # Cerrar puerta
        for p in actuadorPuerta:
            # TODO: Cerrar puerta
            p.angle = 180
            pass

def ventilador(val):
    if val:
        # Prender ventiladores
        for ven in actuadorVentilador:
            gpio.output(12, True)
            # TODO: prender ventilador
            pass
    else:
        # Apagar ventiladores
        for ven in actuadorVentilador:
            gpio.output(12, False)
            # TODO: apagar ventilador
            pass

def aspersor(val):
    if val:
        # Prender aspersores
        for asp in actuadorAspersor:
            # TODO: prender aspersor
            bz.on()
            pass
    else:
        # Apagar aspersores
        for asp in actuadorAspersor:
            # TODO: apagar aspersor
            bz.off()
            pass

def leerSerial():
    # Leemos el serial
    try:
        while True:
            s[0] = str(ser.readline())
            if s[0]:
                print(s[0])
                if str(s[0]).find("cm") != -1:
                    params["distancia"] = s[0][2:str(s[0]).find("cm") + 2]
                elif str(s[0]).find("fotores") != -1:
                    params["luminosidad"] = s[0][str(s[0]).find("fotores") + 9: str(s[0]).find("\\") ]
                elif str(s[0]).find("flamita") != -1:
                    params["flama"] = s[0][str(s[0]).find("flamita") + 9: str(s[0]).find("\\") ] == "1"
                elif str(s[0]).find("Humedad") != -1:
                    params["humedad"] = s[0][str(s[0]).find("Humedad") + 9: str(s[0]).find("%") - 1 ]
                elif str(s[0]).find("Temperatura") != -1:
                    params["temperatura"] = s[0][str(s[0]).find("Temperatura") + 13: str(s[0]).find("\\") ]
                elif str(s[0]).find("mov: ") != -1:
                    params["movimiento"] = int(s[0][str(s[0]).find("mov:") + 5: str(s[0]).find("\\") ]) == 1

    except KeyboardInterrupt:
        pass


def alarma(val):
    if val:
        # Prender alarmas
        for alarm in actuadorAlarma:
            # TODO: prender alarmas
            alarm.on()
            pass
    else:
        # Apagar alarmas
        for alarm in actuadorAlarma:
            # TODO: apagar alarmas
            alarm.off()
            pass
    
# METODO PINCIPAL 
def main():
    threading.Thread(target=leerSerial).start()
    try:
        while True:    
            #print(read_serial)
            # Leemos la distancia
            # params["distancia"] = s[0]
            peticion()
            time.sleep(0.5)
            #print(params)
    except KeyboardInterrupt:
        gpio.cleanup()
        

main()
