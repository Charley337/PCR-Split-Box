import make_data
import calculate
import search
import grammar_analyse
import sys
import os
import json


def proc_config():
    global config
    if len(params) > 0:
        if "=" in params[0]:
            name = params[0].split("=")[0]
            val = params[0].split("=")[1]
            config[name] = val
        elif params[0] == "add":
            try:
                name = params[1]
                val = params[2]
                if val not in config[name]:
                    config[name] += [val]
            except IndexError:
                print("input error")
                return
            except TypeError:
                print("{} is not list".format(name))
                return
        elif params[0] == "remove":
            try:
                name = params[1]
                val = params[2]
                if val in config[name]:
                    config[name].remove(val)
            except IndexError:
                print("input error")
                return
            except AttributeError:
                print("{} is not list".format(name))
                return
        else:
            print("nothing to do")
            return
        with open(config_path, "w", encoding="utf-8") as file:
            json.dump(config, file, ensure_ascii=False)
    for item in config:
        if isinstance(config[item], list):
            print("    {}: [".format(item))
            for i in range(len(config[item])):
                print("        {},".format(config[item][i]))
            print("    ],")
        else:
            print("    {}: {},".format(item, config[item]))


# 初始化配置文件
def init_config():
    global config
    with open(config_path, "r", encoding="utf-8") as file:
        try:
            config = json.load(file)
        except json.decoder.JSONDecodeError:
            config = dict()
            config["stage"] = 1
            config["ban_list"] = ["春猫", "圣千", "圣锤"]
    make_data.config = config
    calculate.config = config
    search.config = config


def main():
    global mode
    global params
    global command
    global config
    command, mode, params = grammar_analyse.argv_analyse(sys.argv)
    if command != "":
        if command in procs:
            procs[command]()
            exit(0)
        else:
            print("invalid command: --{}"
                  "\n    --config : 设置配置文件".format(command))
            exit(-1)
    if len(mode) == 0:
        if os.path.exists("./temp/out_{}.txt".format(config["stage"])):
            search.search(["main.py"] + params, mode=mode)
        else:
            make_data.make_data()
            calculate.calculate()
            search.search(["main.py"] + params, mode=mode)
    else:
        if "m" in mode:
            make_data.make_data()
        if "c" in mode:
            calculate.calculate()
        if "s" in mode or "a" in mode:
            search.search(["main.py"] + params, mode=mode)


config_path = "config.json"

command = ""
mode = set()
params = []
config = dict()
procs = {
    "config": proc_config,
}

if __name__ == "__main__":
    init_config()
    main()

