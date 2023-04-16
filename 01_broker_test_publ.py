from paho.mqtt.client import Client

def main(broker, topic):
    client = Client()

    client.connect(broker)
    client.loop_start()

    while True:
        data  = input('message?')
        client.publish(topic,  data)

if __name__ == "__main__":
    import sys
    if len(sys.argv)<3:
        print(f"Usage: {sys.argv[0]} broker topic")
    broker = sys.argv[1]
    topic = sys.argv[2]
    main(broker, topic)
