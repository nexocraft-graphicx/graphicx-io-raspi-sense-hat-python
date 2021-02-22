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
    config["tenant_identifier"] = enter_credential("TENANT ID", config["tenant_identifier"])
    config["device_identifier"] = enter_credential("DEVICE UUID", config["device_identifier"])
    config["mqtt_broker_url"] = enter_credential("MQTT SERVER URL", config["mqtt_broker_url"])
    config["mqtt_client_username"] = enter_credential("MQTT USERNAME", config["mqtt_client_username"])
    config["mqtt_client_password"] = enter_credential("MQTT PASSWORD", config["mqtt_client_password"])
    return config


def read_config():
    config = {}
    if (os.path.isfile("config_local.json")):
        config_file_path = "config_local.json"
    else:
        config_file_path = "config.json"
    with open(config_file_path) as config_file:
        config_data = json.load(config_file)
        config["tenant_identifier"] = config_data["tenant_identifier"]
        config["device_identifier"] = config_data["device_identifier"]
        config["format_id"] = config_data["format_id"]
        config["compression_id"] = config_data["compression_id"]
        config["mqtt_broker_url"] = config_data["mqtt_broker_url"]
        config["mqtt_client_username"] = config_data["mqtt_client_username"]
        config["mqtt_client_password"] = config_data["mqtt_client_password"]
    return config


def write_config(config):
    data = {}
    data['tenant_identifier'] = config["tenant_identifier"]
    data['device_identifier'] = config["device_identifier"]
    data['format_id'] = "12"
    data['compression_id'] = "02"
    data['mqtt_broker_url'] = config["mqtt_broker_url"]
    data['mqtt_client_username'] = config["mqtt_client_username"]
    data['mqtt_client_password'] = config["mqtt_client_password"]
    with open("config_local.json", "w") as write_file:
        json.dump(data, write_file)


def show_config(config):
    print(
        "tenant_identifier = " + config["tenant_identifier"] + "\n" +
        "device_identifier = " + config["device_identifier"] + "\n" +
        "mqtt_broker_url = " + config["mqtt_broker_url"] + "\n" +
        "mqtt_client_username = " + config["mqtt_client_username"] + "\n" +
        "mqtt_client_password = " + config["mqtt_client_password"] + "\n"
    )


def main():
    print("\nIn the following you can add all important credetials" +
          " to the local cofiguration file for the sample application:\n")

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
