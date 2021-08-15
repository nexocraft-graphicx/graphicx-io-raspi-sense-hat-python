# -*- coding: utf-8 -*-
import json
import os.path


def enter_credential(key, current):
    print("Current " + key + ": " + current + "\n" +
          "If you want to change the " +
          key +
          ", please type it in and press enter. To not change, please let it empty and press enter."
          )
    input_credential = input(("New " + key + ":"))
    if (input_credential == ""):
        input_credential = current
    print("Got it, " + key + " is:" + input_credential + "\n")
    return input_credential


def enter_credentials(config):
    config["mqtt_client_prefix"] = enter_credential("mqtt_client_prefix", config["mqtt_client_prefix"])
    config["device_identifier"] = enter_credential("device_identifier", config["device_identifier"])
    config["mqtt_broker_host"] = enter_credential("mqtt_broker_host", config["mqtt_broker_host"])
    config["mqtt_broker_port"] = enter_credential("mqtt_broker_port", config["mqtt_broker_port"])
    config["mqtt_client_username"] = enter_credential("mqtt_client_username", config["mqtt_client_username"])
    config["mqtt_client_password"] = enter_credential("mqtt_client_password", config["mqtt_client_password"])
    config["mqtt_client_id"] = enter_credential("mqtt_client_id", config["mqtt_client_id"])
    config["use_led_matrix"] = enter_credential("use_led_matrix", config["use_led_matrix"])
    return config


def read_config():
    config = {}
    if (os.path.isfile("config_local.json")):
        config_file_path = "config_local.json"
    else:
        config_file_path = "config.json"
    with open(config_file_path) as config_file:
        config_data = json.load(config_file)
        config["mqtt_client_prefix"] = config_data["mqtt_client_prefix"]
        config["device_identifier"] = config_data["device_identifier"]
        config["format_id"] = config_data["format_id"]
        config["compression_id"] = config_data["compression_id"]
        config["mqtt_broker_host"] = config_data["mqtt_broker_host"]
        config["mqtt_broker_port"] = config_data["mqtt_broker_port"]
        config["mqtt_client_username"] = config_data["mqtt_client_username"]
        config["mqtt_client_password"] = config_data["mqtt_client_password"]
        config["mqtt_client_id"] = config_data["mqtt_client_id"]
        config["use_led_matrix"] = config_data["use_led_matrix"]
    return config


def write_config(config):
    data = {}
    data['mqtt_client_prefix'] = config["mqtt_client_prefix"]
    data['device_identifier'] = config["device_identifier"]
    data['format_id'] = "17"
    data['compression_id'] = "02"
    data['mqtt_broker_host'] = config["mqtt_broker_host"]
    data['mqtt_broker_port'] = config["mqtt_broker_port"]
    data['mqtt_client_username'] = config["mqtt_client_username"]
    data['mqtt_client_password'] = config["mqtt_client_password"]
    data['mqtt_client_id'] = config["mqtt_client_id"]
    data['use_led_matrix'] = config["use_led_matrix"]
    with open("config_local.json", "w") as write_file:
        json.dump(data, write_file)


def show_config(config):
    print(
        "mqtt_client_prefix = " + config["mqtt_client_prefix"] + "\n" +
        "device_identifier = " + config["device_identifier"] + "\n" +
        "mqtt_broker_host = " + config["mqtt_broker_host"] + "\n" +
        "mqtt_broker_port = " + config["mqtt_broker_port"] + "\n" +
        "mqtt_client_username = " + config["mqtt_client_username"] + "\n" +
        "mqtt_client_id = " + config["mqtt_client_id"] + "\n" +
        "use_led_matrix = " + config["use_led_matrix"] + "\n"
    )


def main():
    print("\nIn the following you can add all important credentials" +
          " to the local configuration file for the sample application:\n")

    select = "change"
    while (select == "change"):
        config = read_config()
        config = enter_credentials(config)
        write_config(config)
        show_config(config)
        select = input("Please review the above credentials, if all is correct press ENTER." +
                       " If you want to change them type \"change\" and press ENTER: ")


if __name__ == "__main__":
    main()
