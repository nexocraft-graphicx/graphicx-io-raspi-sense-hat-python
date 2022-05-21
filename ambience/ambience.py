import json
import time
from ledmatrix import thex


def take_and_send_measurements(sense, connection_status, connection_code, mqttc, mqtt_topic_prefix, device_identifier):
    time_epochmillis = int(time.time() * 1000)
    # see https://pythonhosted.org/sense-hat/api/#environmental-sensors
    # degrees Celsius
    temperature_value_raw = sense.get_temperature()
    # scale the measurement which comes from inside the case of the Raspberry Pi
    # in order to obtain measurements similar to usual factory floor temperatures
    temperature_value = (temperature_value_raw * 4.0) - 138.0
    #    temperature_value = 22.22
    # RH percentage
    relative_humidity_value = sense.get_humidity()
    #    relative_humidity_value = 44.44
    # Millibars
    pressure_value = sense.get_pressure()
    #    pressure_value = 1111.11
    send_measurements(sense, connection_status, connection_code, mqttc, mqtt_topic_prefix, device_identifier, time_epochmillis, temperature_value, relative_humidity_value, pressure_value)


def send_measurements(sense, connection_status, connection_code, mqttc, mqtt_topic_prefix, device_identifier, time_epochmillis, temperature_value, relative_humidity_value, pressure_value):
    if (connection_code == 0):
        topic = create_topic_name(mqtt_topic_prefix, device_identifier)
        payload = create_json_payload_dict(sense, time_epochmillis, temperature_value, relative_humidity_value, pressure_value)
        #        print(
        #            "\nTemperature " + (str(temperature_value))
        #            + " Humidity " + (str(relative_humidity_value))
        #            + " Pressure " + (str(pressure_value))
        #        )
        # we use MQTT 3.1.1 QoS 1 and we set the MQTT 3.1.1 retained flag to false
        mqttc.publish(topic, payload, 1, False)
    else:
        print(
            "\nMQTT Server disconnected, can´t send data: " + connection_status[connection_code]
            + "Temperature " + (str(temperature_value))
            + " Humidity " + (str(relative_humidity_value))
            + " Pressure " + (str(pressure_value))
        )


def create_topic_name(mqtt_topic_prefix, device_identifier):
    topic = (
            "" + mqtt_topic_prefix + "/ts/in/" + device_identifier
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


def create_json_payload_dict(sense, time_epochmillis, temperature_value, relative_humidity_value, pressure_value):
    # function for using JSON format TsChannelsFloatSeriesJSON
    try:
        data_dict = initialise_json_data_dict()
        add_float_series_point_to_json_data_dict(data_dict, '1', temperature_value, time_epochmillis)
        add_float_series_point_to_json_data_dict(data_dict, '2', relative_humidity_value, time_epochmillis)
        add_float_series_point_to_json_data_dict(data_dict, '3', pressure_value, time_epochmillis)
        payload_dict = {'data': data_dict}
        payload_json = json.dumps(payload_dict)
        # if this would not use the simple default payload format (see graphicx.io quickstart)
        # the following would be done to include a format_id and a compression_id
        # moreover with MQTT v5 these would become custom headers on the MQTT message
        #        payload = bytes.fromhex(format_id) + bytes.fromhex(compression_id) + bytearray(payload_json, "utf8")
        payload = bytearray(payload_json, "utf8")
    except:
        thex.the_x_in_red(sense)
        raise
    return payload
