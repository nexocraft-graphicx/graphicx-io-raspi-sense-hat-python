# -*- coding: utf-8 -*-
import json
import os.path
import threading
import time

from sense_hat import SenseHat

import paho.mqtt.client as mqtt

mqttc = mqtt.Client("raspidemo1_localwithmockedsensehat", True, None, mqtt.MQTTv311, "tcp")
# mqttc = mqtt.Client("raspidemo1_localwithmockedsensehat", None, None, mqtt.MQTTv5, "tcp")

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

# ----- MQTT Client -----

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
    if (connection_code != 0):
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
        raise ValueError(
            "Not able to initiate MQTT connection. Please check format of login parameters incl. server URL.")


def disconnect_mqtt():
    mqttc.loop_stop()
    mqttc.disconnect()


# ----- Timer for regularly measuring and sending values to graphicx.io -----

def timer_measurement():
    try:
        thread = threading.Timer(3, timer_measurement)
        thread.daemon = True
        thread.start()
        take_and_send_measurements()
        while True: time.sleep(100)
    except (KeyboardInterrupt, SystemExit):
        disconnect_mqtt()
        print("Stopping loop, disconnecting from MQTT server and quitting.")


# ----- Functions -----

def take_and_send_measurements():
    time_epochmillis = int(time.time() * 1000)
    # see https://pythonhosted.org/sense-hat/api/#environmental-sensors
    # degrees Celsius
    temperature_value = sense.get_temperature()
    # RH percentage
    relative_humidity_value = sense.get_humidity()
    # Millibars
    pressure_value = sense.get_pressure()
    send_measurements(time_epochmillis, temperature_value, relative_humidity_value, pressure_value)


def send_measurements(time_epochmillis, temperature_value, relative_humidity_value, pressure_value):
    if (connection_code == 0):
        topic = create_topic_name()
        payload = create_json_payload_dict(time_epochmillis, temperature_value, relative_humidity_value, pressure_value)
        #        print(
        #            "\nTemperature " + (str(temperature_value))
        #            + " Humidity " + (str(relative_humidity_value))
        #            + " Pressure " + (str(pressure_value))
        #        )
        mqttc.publish(topic=topic, payload=payload, qos=1, retain=False)
    else:
        print(
            "\nMQTT Server disconnected, can´t send data: " + connection_status[connection_code]
            + "Temperature " + (str(temperature_value))
            + " Humidity " + (str(relative_humidity_value))
            + " Pressure " + (str(pressure_value))
        )


# def create_payload_proto(temperature_value, relative_humidity_value, device_identifier):
#    try:
#        data_proto = DataInChannelsAtTimeFloatProto3.device_data()
#        data_proto.device_identifier = device_identifier
#        data_proto.time = int(time.time()*1000)
#        data_proto.data[1] = temperature_value
#        data_proto.data[2] = relative_humidity_value
#        payload = bytes.fromhex(format_id) + bytes.fromhex(compression_id) + data_proto.SerializeToString()
#    except:
#        raise ValueError ("Payload creation failed (protobuf)")
#    return payload


def create_topic_name():
    topic = (
            "tenant/" + tenant_identifier + "/ts/in/" + device_identifier
    )
    #    print("\nMQTT topic: " + topic)
    return topic


def initialise_json_data_dict():
    # function for using JSON format TsChannelsFloatSeriesJSON
    data_dict = {'1': [], '2': [], '3': []}
    # will use three Channels, one for each datapoint
    return data_dict


def add_float_series_point_to_json_data_dict(data_dict, channel, value, time_epochmillis):
    # function for using JSON format TsChannelsFloatSeriesJSON
    float_series_point = {"time": time_epochmillis, "value": value}
    data_dict[channel].append(float_series_point)
    return data_dict


def create_json_payload_dict(time_epochmillis, temperature_value, relative_humidity_value, pressure_value):
    # function for using JSON format TsChannelsFloatSeriesJSON
    try:
        data_dict = initialise_json_data_dict()
        add_float_series_point_to_json_data_dict(data_dict, '1', temperature_value, time_epochmillis)
        add_float_series_point_to_json_data_dict(data_dict, '2', relative_humidity_value, time_epochmillis)
        add_float_series_point_to_json_data_dict(data_dict, '3', pressure_value, time_epochmillis)
        payload_dict = {'data': data_dict}
        payload_json = json.dumps(payload_dict)
        payload = bytes.fromhex(format_id) + bytes.fromhex(compression_id) + bytearray(payload_json, "utf8")
    except:
        raise ValueError("Payload creation failed (JSON)")
    return payload


# Sense Hat
sense = SenseHat()
sense.clear()

# MQTT client
mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_disconnect = on_disconnect
mqttc.on_publish = on_publish
mqttc.on_log = on_log


def main():
    print(
        "Example grapicx.io IoT platform\n\n"
        "tenant_identifier = " + tenant_identifier + "\n" +
        "device_identifier = " + device_identifier + "\n" +
        "format_id = " + format_id + "\n" +
        "compression_id = " + compression_id + "\n" +
        "mqtt_broker_host = " + mqtt_broker_host + "\n" +
        "mqtt_broker_port = " + str(mqtt_broker_port) + "\n" +
        "mqtt_client_username = " + mqtt_client_username + "\n"
    )
    connect_mqtt()
    while (connection_code != 0):
        pass
    print("\nStart transmission. Exit with Ctrl+C")
    timer_measurement()


if __name__ == "__main__":
    main()
