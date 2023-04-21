import paho.mqtt.publish as publish
import sys

from paho.mqtt.client import Client
from multiprocessing import Process, Manager, Value, Lock
from time import sleep
from random import randint

UPPER_TIMER=10 # integer > 2, upper limit for timer set up

LOWER_TEMP=10
UPPER_TEMP=15

LOWER_HUM=20
UPPER_HUM=30


def is_prime(n):
    i = 2
    while i*i < n and n % i != 0:
        i += 1
    return i*i > n

def in_range(pid,data,factor):
    mutex='locks'
    
    try:
        data[mutex]['datos'].acquire()
        suma=sum(data['datos'][pid][factor])
        avg=suma/len(data['datos'][pid][factor])
        data[mutex]['datos'].release()
        
        if factor==0:
            print(f'{pid}, Avg temp: {avg}')
        else:
            print(f'{pid}, Avg hum: {avg}')
            
        return data[factor][0]<avg and avg<data[factor][1]
    
    except ZeroDivisionError:
        data[mutex]['datos'].release()
        print(f'{pid}, Not enough data')
        return False

def f_timer(pid,data,broker):
    t=randint(2,UPPER_TIMER)
    print(f'Timer for proccess {pid} is {t}')
    text_1=f'timer has started,{pid}'
    text_2=f'timeout,{pid}'
    
    publish.single('temperature/t1', payload=text_1, hostname=broker)
    sleep(t)
    publish.single('temperature/t1', payload=text_2, hostname=data['broker'])
    
    if not in_range(pid,data,0):
        publish.single('humidity', payload=text_1, hostname=data['broker'])
        sleep(t)
        publish.single('humidity', payload=text_2, hostname=data['broker'])
        
        if in_range(pid,data,1):
            print(f'From {pid}: Temperature out of range, but Humidity in Range')
        else:
            print(f'From {pid}: ALERT, Temperature and Humidity out of range')
            
    else:
        print(f'From {pid}: Temperature in range')
    

def on_message_1(mqttc, data, msg):
    mutex='locks'
    try:
        d = float(msg.payload)
        n = int(round(d))
        
        if n==d and n>1 and is_prime(n) :
            data[mutex]['datos'].acquire()
            data['datos'].append(([],[]))
            data[mutex]['datos'].release()
            
            data[mutex]['pid'].acquire()
            pid=data['pid'].value
            print(f'Starting process {pid}')
            data['pid'].value = pid+1
            data[mutex]['pid'].release()
            
            worker=Process(target=f_timer,args=(pid,data,'simba.fdi.ucm.es'))
            worker.start()
            
    except ValueError:
        pass
        
def on_message_2(mqttc, data, msg):
    print(msg.payload)
    mensaje=str(msg.payload).split(',')
    mutex='locks'
    conjunto=data['objetivo']
    
    target=0
    if conjunto == 'active_pid_hum':
        target=1
        
    if len(mensaje)>1:
        data[mutex][conjunto].acquire()
        if mensaje[0]=='time has started':
            print(mensaje)
            data[conjunto][int(mensaje[1][2:-1])]=1
        elif mensaje[0]=='timeout':
            del data[conjunto][int(mensaje[1][2:-1])]
        data[mutex][conjunto].release()
        
    else:
        data[mutex]['datos'].acquire()
        for pid in data[conjunto]:
            print('anadiendo')
            datos[pid][target].append(int(msg.payload))
        data[mutex]['datos'].release()

def main(hostname):
    manager=Manager()
    lock=Lock()
    
    datos = manager.list()
    pid = Value('i',0)
    active_pid_temp = manager.dict()
    active_pid_hum = manager.dict()
    
    locks={}
    locks['datos']=lock
    locks['pid']=lock
    locks['active_pid_temp']=lock
    locks['active_pid_hum']=lock

    data={'broker':hostname,
          'datos':datos,
          'pid':pid,
          'active_pid_temp':active_pid_temp,
          0:[LOWER_TEMP,UPPER_TEMP],
          'active_pid_hum':active_pid_hum,
          1:[LOWER_HUM,UPPER_HUM],
          'locks':locks}
    
    mqttc1 = Client(userdata=data)
    mqttc1.on_message = on_message_1
    mqttc1.connect(hostname)
    mqttc1.subscribe('numbers')
    mqttc1.loop_start()

    data['objetivo']='active_pid_temp'

    mqttc2 = Client(userdata=data)
    mqttc2.on_message = on_message_2
    mqttc2.connect(hostname)
    mqttc2.subscribe('temperature/#')
    mqttc2.loop_start()

    data['objetivo']='active_pid_hum'
    
    mqttc3 = Client(userdata=data)
    mqttc3.on_message = on_message_2
    mqttc3.connect(hostname)
    mqttc3.subscribe('humidity')
    mqttc3.loop_forever()

if __name__ == '__main__':
    hostname = 'simba.fdi.ucm.es'
    if len(sys.argv)>1:
        hostname = sys.argv[1]
    main(hostname)
