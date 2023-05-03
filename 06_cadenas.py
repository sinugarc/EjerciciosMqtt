import paho.mqtt.publish as publish
import sys

from paho.mqtt.client import Client
from multiprocessing import Process, Manager, Value, Lock
from time import sleep
from random import randint

UPPER_TIMER=10 # integer > 3, upper limit for timer set up

LOWER_TEMP=10
UPPER_TEMP=15

LOWER_HUM=30
UPPER_HUM=70


def in_range(pid,data,factor):
    """
    Funcion que calcula si los datos de un {pid} dado un factor (temp/hum)
    estan entre los limites estipulados encima.

    Tiene en cuenta la posibilidad de tener 0 datos, por eso la excepcion.

    Saca por pantalla la temp/hum media
    """
    
    mutex='locks'
    
    try:
        name=str(pid)+'_'+factor
        data[mutex]['datos'].acquire()
        suma=sum(data['datos'][name])
        avg=suma/len(data['datos'][name])
        data[mutex]['datos'].release()
        
        if factor=='temp':
            print(f'Process {pid}, Avg temp: {avg}')
        else:
            print(f'Process {pid}, Avg hum: {avg}')

        return data[factor][0]<avg and avg<data[factor][1]
    
    except ZeroDivisionError:
        data[mutex]['datos'].release()
        print(f'Process {pid}, Not enough data')
        return False

def f_timer(pid,data):
    """
    Funcion objetivo del proceso. Una vez llamada se ejecuta un temporizador para
    almacenar las temperaturas y se calcula si estan o no en rango.

    Si no lo estan vuelve a activar un temporizador para almacenar la humedad y
    calcula si estan en rango.

    Devuelve por pantalla los resultados del rango y ademas antes de finalizar
    hace un print de los datos, aunque no sea necesario, pero que sirve para
    observar como los almacena.
    
    """
    
    mutex='locks'
    t=randint(3,UPPER_TIMER)
    print(f'Timer for process {pid} is {t}')
    text_1=f'timer has started,{pid}'
    text_2=f'timeout,{pid}'
    
    publish.single('/clients/timer', payload=text_1+',temp', hostname=data['broker'])
    sleep(t)
    publish.single('/clients/timer', payload=text_2+',temp', hostname=data['broker'])
    
    
    if not in_range(pid,data,'temp') :
        
        publish.single('/clients/timer', payload=text_1+',hum', hostname=data['broker'])
        sleep(t)
        publish.single('/clients/timer', payload=text_2+',hum', hostname=data['broker'])
        
        if in_range(pid,data,'hum'):
            print(f'From process {pid}: Temperature out of range, but Humidity in Range')
        else:
            print(f'From process {pid}: ALERT, Temperature and Humidity out of range')
            
    else:
        print(f'From process {pid}: Temperature in range')

    print(f'Full data once process {pid} has finished:\n',data['datos'])
    

def on_message_1(mqttc, data, msg):
    """
    Funcion on_message del primer cliente subscrito a numbers.

    Cada vez que recibe un numero entero mayor que 1 par, inicia un proceso para
    el calculo de temp/hum.
    
    """
    mutex='locks'
    try:
        d = float(msg.payload)
        n = int(round(d))
        
        if n==d and n>1 and n%2==0:
            data[mutex]['pid'].acquire()
            pid=data['pid'].value
            data['pid'].value = pid+1
            data[mutex]['pid'].release()

            print(f'Starting process {pid}')
            worker=Process(target=f_timer,args=(pid,data))
            worker.start()
            
    except ValueError:
        pass
        
def on_message_2(mqttc, data, msg):
    """
    Funcion on_message del segundo cliente, subscrito a temperature/#, humidity
    y al topic del temporizador.

    Primero localiza el topic del que recibe el mensaje, ya sea de temp y/o humedad
    y sus repectivos temporizadores.

    Si detecta un temporizador, detecta el {pid} del proceso y, o lo pone
    en el diccionario que indica si debe guardar informacion o lo quita de este mismo.

    Solo cuando el diccionario adecuado no este vacio, procesara la temperatura/humedad
    y la guardara tantas veces como sea necesario.
    
    """
    
    mensaje=str(msg.payload).split(',')
    mutex='locks'
    timer=''
    
    if len(mensaje)>1:
        timer = mensaje[2][0:-1] # Detecta si el timer es para temp o hum

    if msg.topic == 'humidity' or timer == 'hum': # Detecta que objetivo y conjunto debe usar
        target = 'hum'
        conjunto = 'active_pid_hum'
    else:
        target = 'temp'
        conjunto = 'active_pid_temp'
    
    if len(mensaje)>1: # Se encuentra con un mensaje del temporizador
        data[mutex][conjunto].acquire()
        if mensaje[0][2:]=='timer has started':
            name=(mensaje[1])+'_'+target # Da nombre al diccionario que contendra la informacion
            data[conjunto][name]=1 # Lo añade al diccionario del conjunto
        elif mensaje[0][2:]=='timeout':
            name=(mensaje[1])+'_'+target
            del data[conjunto][name] # Una vez el temporizador acaba, lo elimina del conjunto
        data[mutex][conjunto].release()
        
    elif len(data[conjunto]) != 0: # Detecta si hay algun temporizador activo y guarda el dato
        data[mutex]['datos'].acquire()
        for pid in data[conjunto]:
            if pid in data['datos']:
                l=data['datos'][pid]
                l.append(int(msg.payload))
                data['datos'][pid]=l
            else: #Si es la primera vez que añade dato para ese pid, crea la lista de temp o hum.
                data['datos'][pid]=[int(msg.payload)]
        data[mutex]['datos'].release()

def main(hostname):
    manager=Manager()
    lock=Lock()
    
    datos = manager.dict()
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
          'temp':[LOWER_TEMP,UPPER_TEMP],
          'active_pid_hum':active_pid_hum,
          'hum':[LOWER_HUM,UPPER_HUM],
          'locks':locks}
    
    mqttc1 = Client(userdata=data)
    mqttc1.on_message = on_message_1
    mqttc1.connect(hostname)
    mqttc1.subscribe('numbers')
    mqttc1.loop_start()

    mqttc2 = Client(userdata=data)
    mqttc2.on_message = on_message_2
    mqttc2.connect(hostname)
    mqttc2.subscribe('temperature/#')
    mqttc2.subscribe('humidity')
    mqttc2.subscribe('/clients/timer')
    mqttc2.loop_forever()

if __name__ == '__main__':
    hostname = 'simba.fdi.ucm.es'
    if len(sys.argv)>1:
        hostname = sys.argv[1]
    main(hostname)
