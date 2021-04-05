# -*- coding: utf-8 -*-
import json
import os.path


# Platform, mqqt and device parameters (read form "config.json" if "config_local.json" is not available (.gitignore))
if (os.path.isfile("config_local.json")):
    config_file_path = "config_local.json"
else:
    config_file_path = "config.json"

with open(config_file_path) as config_file:
    config_data = json.load(config_file)


def get_config_data():
    return config_data


def get_use_led_matrix():
    use_led_matrix_config_value = config_data["use_led_matrix"]
    return (use_led_matrix_config_value == 'True' or use_led_matrix_config_value == 'true')
