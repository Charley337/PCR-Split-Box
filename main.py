import make_data
import calculate
import search
import sys
import os
import json


# 初始化配置文件
def init_config():
    global config
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
    make_data.config = config
    calculate.config = config
    search.config = config


# 判断单个字符是否是英文字母
def is_alpha(ch):
    ord_ch = ord(ch)
    ord_a = ord("a")
    ord_aa = ord("A")
    if (ord_a <= ord_ch <= ord_a + 25) or (ord_aa <= ord_ch <= ord_aa + 25):
        return True
    else:
        return False


# 判断单个字符是否是数字
def is_digit(ch):
    ord_0 = ord("0")
    if ord_0 <= ord(ch) <= ord_0 + 9:
        return True
    else:
        return False


# 错误处理程序
def error_handle(arg, errcode=-1, msg=""):
    if errcode == -1:
        print("[error] error occur\n    " + msg + ": " + arg)
    exit(-1)


# 词法分析 —— 得到每个arg的类别
def get_arg_type(arg):
    state = 0
    for i in range(len(arg)):
        if state == 0:
            if arg[i] == "-":
                state = 1
            else:
                state = 4
        elif state == 1:
            if arg[i] == "-":
                state = 2
            elif is_alpha(arg[i]):
                state = 3
        elif state == 2:
            if is_alpha(arg[i]) or is_digit(arg[i]):
                pass
            else:
                error_handle(arg, msg="command syntax error")
        elif state == 3:
            if is_alpha(arg[i]):
                pass
            else:
                error_handle(arg, msg="mode syntax error")
        elif state == 4:
            pass
        else:
            error_handle(arg, msg="state error")
    if state == 2:
        return "command"
    elif state == 3 or state == 1:
        return "mode"
    elif state == 4:
        return "arg"
    else:
        error_handle(arg, msg="fail to find type")
        return "error"


# 语法分析
def argv_analyse():
    global mode
    global param
    global command
    global config
    for i in range(1, len(sys.argv)):
        if get_arg_type(sys.argv[i]) == "command":
            command.add(sys.argv[i][2:])
        elif get_arg_type(sys.argv[i]) == "mode":
            mode.add(sys.argv[i][1:])
        elif get_arg_type(sys.argv[i]) == "arg":
            param.append(sys.argv[i])


def main():
    global mode
    global param
    global command
    global config
    argv_analyse()


mode = set()
command = set()
param = []
config = dict()

if __name__ == "__main__":
    init_config()
    main()

