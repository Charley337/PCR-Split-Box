import json


# init config
def init_config(config):
    with open("config.json", "r", encoding="utf-8") as file:
        try:
            config = json.load(file)
        except json.decoder.JSONDecodeError:
            # config = dict()
            # config["stage"] = 1
            # config["ban_list"] = ["春猫", "圣千", "圣锤"]
            print("fail to config, please check your config file")
            exit(-1)
    return config


# check config
def check_config(config):
    if len(config) == 0:
        config = init_config(config)
    return config

