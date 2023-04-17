import paho.mqtt.publish as publish
import sys

from paho.mqtt.client import Client
from multiprocessing import Process, Manager
from time import sleep
from random import randint

UPPER_TIMER=10 # integer > 2, upper limit for timer set up

LOWER_TEMP=10
UPPER_TEMP=15

LOWER_HUM=20
UPPER_HUM=30

datos=[]
pid=[]

active_pid_temp=set()
active_pid_hum=set()


def is_prime(n):
    i = 2
    while i*i < n and n % i != 0:
        i += 1
    return i*i > n

def temp_range(pid):
    try:
        suma=sum(datos[pid][0])
        avg=suma/len(datos[pid][0])
        print(f'{pid}, Avg temp: {avg}')
        return LOWER_TEMP<avg and avg<UPPER_TEMP
    except ZeroDivisionError:
        print(f'{pid}, Not enough temp data')
        return False

def hum_range(pid):
    try:
        suma=sum(datos[pid][1])
        avg=suma/len(datos[pid][1])
        print(f'{pid}, Avg hum: {avg}')
        return LOWER_HUM<avg and avg<UPPER_HUM
    except ZeroDivisionError:
        print(f'{pid}, Not enough hum data')
        return False

def f_timer(mqttc, pid):
    t=randint(2,UPPER_TIMER)
    mqttc.publish('temperature/t1',f'timer has started,{pid}')
    sleep(t)
    mqttc.publish('temperature/t1',f'timeout,{pid}')
    sleep(1)
    if not temp_range(pid):
        mqttc.publish('humidity',f'timer has started,{pid}')
        sleep(t)
        mqttc.publish('humidity',f'timeout,{pid}')
        sleep(1)
        if hum_range(pid):
            print(f'From {pid}: Temperature out of range, but Humidity in Range')
        else:
            print(f'From {pid}: ALERT, Temperature and Humidity out of range')
    else:
        print(f'From {pid}: Temperature in range')
    

def on_message_1(mqttc, data, msg):
    print(msg.payload)
    try:
        d = float(msg.payload)
        print(d)
        n = int(round(d))
        if n==d and n>1 and is_prime(n) :
            datos.append(([],[]))
            worker=Process(target=f_timer,args=(mqttc,len(pid)))
            worker.start()
            pid.append(1)
    except ValueError:
        pass
        
def on_message_2(mqttc, data, msg):
    print(msg.payload)
    mensaje=str(msg.payload).split(',')
    if len(mensaje)>1:
        if mensaje[0]=='time has started':
            active_pid_temp.add(int(mensaje[1][2:-1]))
            print(active_pid_temp)
        elif mensaje[0]=='timeout':
            active_pid_temp.remove(int(mensaje[1][2:-1]))
            print(active_pid_temp)
    else:
        for pid in active_pid_temp:
            datos[pid][0].append(int(msg.payload))
            
def on_message_3(mqttc, data, msg):
    print(msg.payload)
    mensaje=str(msg.payload).split(',')
    if len(mensaje)>1:
        if mensaje[0]=='time has started':
            active_pid_hum.add(int(mensaje[1][2:-1]))
        elif mensaje[0]=='timeout':
            active_pid_hum.remove(int(mensaje[1][2:-1]))
    else:
        for pid in active_pid_hum:
            datos[pid][1].append(int(msg.payload))


def main(hostname):
    
    mqttc1 = Client()
    mqttc1.on_message = on_message_1
    mqttc1.connect(hostname)
    mqttc1.subscribe('numbers')
    mqttc1.loop_start()

    mqttc2 = Client()
    mqttc2.on_message = on_message_2
    mqttc2.connect(hostname)
    mqttc2.subscribe('temperature/#')
    mqttc2.loop_start()

    mqttc3 = Client()
    mqttc3.on_message = on_message_3
    mqttc3.connect(hostname)
    mqttc3.subscribe('humidity')
    mqttc3.loop_forever()

if __name__ == '__main__':
    hostname = 'simba.fdi.ucm.es'
    if len(sys.argv)>1:
        hostname = sys.argv[1]
    main(hostname)
