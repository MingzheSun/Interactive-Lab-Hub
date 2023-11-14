import qwiic_keypad
import time
import sys
import paho.mqtt.client as mqtt
import uuid
import ssl

# MQTT setup
client = mqtt.Client(str(uuid.uuid1()))
client.tls_set(cert_reqs=ssl.CERT_NONE)
client.username_pw_set('idd', 'device@theFarm')
client.connect('farlab.infosci.cornell.edu', port=8883)
topic = 'IDD/food_water_dispenser'

def runExample():
    print("\nkeypad started\n")
    myKeypad = qwiic_keypad.QwiicKeypad()

    if myKeypad.is_connected() == False:
        print("The Qwiic Keypad device isn't connected to the system. Please check your connection", file=sys.stderr)
        return

    myKeypad.begin()

    while True:
        myKeypad.update_fifo()  
        button = myKeypad.get_button()

        if button == -1:
            print("No keypad detected")
            time.sleep(1)

        elif button != 0:
            charButton = chr(button)
            print(f"Button {charButton} pressed")

            if charButton == '1':
                client.publish(topic, "dispensing food")
            elif charButton == '2':
                client.publish(topic, "dispensing water")
            elif charButton == '3':
                client.publish(topic, "petting")
            elif charButton == '4':
                client.publish(topic, "calling owner")
            elif charButton == '5':
                client.publish(topic, "press to talk")
            elif charButton == '6':
                client.publish(topic, "cleaning litter")
            else:
                client.publish(topic, f"Button {charButton} pressed")

            sys.stdout.flush()

        time.sleep(.25)

runExample()
