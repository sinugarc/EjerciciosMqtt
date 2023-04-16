from paho.mqtt.client import Client
from time import sleep
import sys

SLEEP_TIME=10

numeros=[]
enteros=[]
reales=[]
primos=[]

def is_prime(n):
    i = 2
    while i*i < n and n % i != 0:
        i += 1
    return i*i > n

def add(number):
    numeros.append(number)
    if type(number)==int:
        enteros.append(number)
        if is_prime(number):
            primos.append(number)
    elif type(number)==float:
        reales.append(number)

def update():
    num=len(numeros)
    ent=len(enteros)
    real=len(reales)
    pr=len(primos)
    print(f'{num} numbers have been processed, {real} are float and {ent} are integers. {pr} of {ent} integers are primes')
    print(f'Floats: {reales} \nIntegers: {enteros} \nPrime: {primos}')

def on_message(mqttc, userdata, msg):
    try:
        d = float(msg.payload)
        n = int(round(d))
        if n==d:
            add(n)
        else:
            add(d)
    except ValueError:
        pass

def main(hostname):
    mqttc = Client()
    mqttc.on_message = on_message
    mqttc.connect(hostname)
    mqttc.subscribe('numbers')
    mqttc.loop_start()

    while True:
        sleep(SLEEP_TIME)
        update()

if __name__ == '__main__':
    hostname = 'simba.fdi.ucm.es'
    if len(sys.argv)>1:
        hostname = sys.argv[1]
    main(hostname)
