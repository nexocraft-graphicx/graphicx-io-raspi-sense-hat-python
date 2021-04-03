# -*- coding: utf-8 -*-
import json
import os.path
import threading
import time
import os

from sense_hat import SenseHat

import paho.mqtt.client as mqtt

from ambience import ambience
from ledmatrix import thex

# ----- Sense Hat -----

sense = SenseHat()

# ----- Configuration -----

# Platform, mqqt and device parameters (read form "config.json" if "config_local.json" is not available (.gitignore))
if (os.path.isfile("config_local.json")):
    config_file_path = "config_local.json"
else:
    config_file_path = "config.json"

with open(config_file_path) as config_file:
    config_data = json.load(config_file)
    tenant_identifier = config_data["tenant_identifier"]
    device_identifier = config_data["device_identifier"]
    format_id = config_data["format_id"]
    compression_id = config_data["compression_id"]
    mqtt_broker_host = config_data["mqtt_broker_host"]
    mqtt_broker_port = int(config_data["mqtt_broker_port"])
    mqtt_client_username = config_data["mqtt_client_username"]
    mqtt_client_password = config_data["mqtt_client_password"]
    mqtt_client_id = config_data["mqtt_client_id"]

# ----- MQTT Client -----

mqttc = mqtt.Client(mqtt_client_id, True, None, mqtt.MQTTv311, "tcp")
# mqttc = mqtt.Client("raspidemo1_mqtt_client", None, None, mqtt.MQTTv5, "tcp")

connection_status = [
    "Connection successful",
    "Connection refused – incorrect protocol version",
    "Connection refused – invalid client identifier",
    "Connection refused – server unavailable",
    "Connection refused – bad username or password",
    "Connection refused – not authorised",
    "Connection status not initialised"
]

# Status code of MQTT server connection 
connection_code = -1


# Define event callbacks
def on_disconnect(client, userdata, rc):
    global connection_code
    connection_code = rc
    if rc != 0:
        print("Connection code " + str(rc) + ": " + connection_status[connection_code])


def on_connect(client, userdata, flags, rc):
    global connection_code
    connection_code = rc
    print("Connection code " + str(rc) + ": " + connection_status[connection_code])


def on_publish(client, obj, mid):
    print("Published mid: " + str(mid))


def on_log(client, obj, level, string):
    print("Log: " + string)


# MQTT
def connect_mqtt():
    try:
        print("Configuring MQTT Client...")

        # this makes the MQTT Client behave like a web browser regarding TLS
        # see paho API documentation for details
        # https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php
        mqttc.tls_set(None, None, None, mqtt.ssl.CERT_REQUIRED, mqtt.ssl.PROTOCOL_TLSv1_2, None)
        mqttc.tls_insecure_set(False)

        mqttc.username_pw_set(mqtt_client_username, mqtt_client_password)
        mqttc.reconnect_delay_set(1, 60)
        mqttc.message_retry_set(10)

        print("Connecting to MQTT Client...")
        mqttc.connect_async(mqtt_broker_host, mqtt_broker_port, 30)
        mqttc.loop_start()
    except:
        thex.the_x_in_red(sense)
        raise ValueError(
            "Not able to initiate MQTT connection. Please check format of login parameters incl. server URL.")


def disconnect_mqtt():
    print("If not yet done stopping MQTT Client gracefully.")
    mqttc.loop_stop()
    mqttc.disconnect()


mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.on_log = on_log


# ----- Timer for regularly measuring and sending values to graphicx.io -----

def our_loop_in_one_thread():
    try:
        # time.time() returns EpochSeconds
        next_call = time.time()
        sense.set_imu_config(True, True, False)
        while True:
            thex.the_x_lit(sense)
            ambience.take_and_send_measurements(sense, connection_status, connection_code, mqttc, tenant_identifier,
                                                device_identifier)
            time.sleep(5)
            # next call in 30 seconds
            next_call = next_call + 30
            seconds_to_sleep = max(0.0, next_call - time.time())
            thex.the_x_dimmed(sense)
            time.sleep(seconds_to_sleep)
    except (KeyboardInterrupt):
        thex.the_x_in_yellow(sense)
        print("KeyboardInterrupt caught in our loop.")
    except (SystemExit):
        thex.the_x_in_yellow(sense)
        print("SystemExit caught in our loop.")
        disconnect_mqtt()
    except:
        thex.the_x_in_red(sense)
        raise
    finally:
        disconnect_mqtt()
        time.sleep(7)
        os._exit(1)


# ----- Functions -----


def main():
    time.sleep(1)
    thex.the_x_off(sense)
    sense.low_light = True
    time.sleep(2)
    sense.set_imu_config(True, True, False)
    time.sleep(1)
    sense.get_compass_raw()
    time.sleep(1)
    sense.get_compass()
    time.sleep(1)
    sense.get_orientation_degrees()
    time.sleep(2)
    thex.the_x_vague(sense)
    try:
        print(
            "Example grapicx.io IoT platform\n\n"
            "tenant_identifier = " + tenant_identifier + "\n" +
            "device_identifier = " + device_identifier + "\n" +
            "format_id = " + format_id + "\n" +
            "compression_id = " + compression_id + "\n" +
            "mqtt_broker_host = " + mqtt_broker_host + "\n" +
            "mqtt_broker_port = " + str(mqtt_broker_port) + "\n" +
            "mqtt_client_username = " + mqtt_client_username + "\n"
                                                               "mqtt_client_id = " + mqtt_client_id + "\n"
        )
        connect_mqtt()
        time.sleep(12)
        if (connection_code != 0):
            print("Could not connect to MQTT Broker within 12 seconds." +
                  " Exiting program so that it will be restarted.\n")
            thex.the_x_in_red(sense)
            time.sleep(10)
            pass
        else:
            print("Starting data collection loop in another thread.\n")
            timer_thread = threading.Thread(target=our_loop_in_one_thread)
            timer_thread.daemon = True
            timer_thread.start()

            while True:
                time.sleep(10)
    except (KeyboardInterrupt):
        thex.the_x_in_yellow(sense)
        print("KeyboardInterrupt caught in main.")
        disconnect_mqtt()
    except (SystemExit):
        thex.the_x_in_yellow(sense)
        print("SystemExit caught in main.")
        disconnect_mqtt()
    except:
        thex.the_x_in_red(sense)
        raise
    finally:
        print("Exiting from main.")
        disconnect_mqtt()
        time.sleep(10)
        thex.the_x_off(sense)
        time.sleep(1)


if __name__ == "__main__":
    main()
