from paho.mqtt.client import Client
from time import sleep
import sys

SLEEP_TIME=8

temperaturas={}

def update():
    t_max=[]
    t_min=[]
    total_med=0
    total=0
    if temperaturas != {}:
        for sid in temperaturas:
            t_max.append(max(temperaturas[sid]))
            t_min.append(min(temperaturas[sid]))
            mediciones = len(temperaturas[sid])
            suma = sum(temperaturas[sid])
            t_mu=suma/mediciones
            total_med += mediciones
            total += suma
            print(f'Sensor {sid} has reached: Max={t_max[-1]:.2f}, Min={t_min[-1]:.2f} and Avg={t_mu:.2f}')
        maximo=max(t_max)
        minimo=min(t_min)
        t_mu=total/total_med
        print(f'Global temperatures: Max={maximo:.2f}, Min={minimo:.2f} and Avg={t_mu:.2f}')
    else:
        print("No temperature has been recorded yet")

def on_message(mqttc, userdata, msg):
    t=float(msg.payload)
    sid=msg.topic.split("/")[1]
    if sid in temperaturas:
        temperaturas[sid].append(t)
    else:
        temperaturas[sid]=[t]

def main(hostname):
    mqttc = Client()
    mqttc.on_message = on_message
    mqttc.connect(hostname)
    mqttc.subscribe('temperature/#')
    mqttc.loop_start()

    while True:
        sleep(SLEEP_TIME)
        update()

if __name__ == '__main__':
    hostname = 'simba.fdi.ucm.es'
    if len(sys.argv)>1:
        hostname = sys.argv[1]
    main(hostname)
