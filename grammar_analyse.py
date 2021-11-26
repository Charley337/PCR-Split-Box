import sys


# 错误处理程序
def error_handle(errcode=-1, msg=""):
    global error_dict
    if errcode == error_dict["<default error>"]:
        print("[error {}] <default error> ".format(errcode) + msg)
        exit(errcode)
    elif errcode == error_dict["<syntax error>"]:
        print("[error {}] <syntax error> ".format(errcode) + msg)
        exit(errcode)


def get_type_and_num(s):
    if s[0] == "s":
        return "shift", int(s[6:])
    elif s[0] == "r":
        return "reduce", int(s[7:])
    elif s[0] == "a":
        return "accept", -1
    else:
        return "goto", int(s)


# 分析表初始化
def analysis_init():
    global analysis
    global lr1_path
    with open(lr1_path, "r") as fp:
        buf = fp.read()
    buf = buf.split("\n")
    for i in range(len(buf)):
        buf[i] = buf[i].split(",")
    divide = -1
    for j in range(len(buf[0])):
        if buf[0][j] == "GOTO":
            divide = j
    if divide == -1:
        error_handle(msg="divide == {}".format(divide))
    for i in range(2, len(buf)):
        for j in range(1, len(buf[i])):
            if buf[i][j] != "":
                if j < divide:
                    table = "action"
                else:
                    table = "goto"
                t, n = get_type_and_num(buf[i][j])
                analysis["{},{},{}".format(table, i - 2, buf[1][j])] = (t, n)


def grammar_init():
    global grammar
    with open(grammar_path, "r") as fp:
        grammar = fp.read()
    grammar = grammar.split("\n")


def stack_init():
    global state_stack
    global sym_stack
    state_stack = [0]
    sym_stack = ["#"]


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


# 词法分析 —— 得到每个arg的类别
def get_argv_token(arg):
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
                error_handle(msg="command syntax error")
        elif state == 3:
            if is_alpha(arg[i]):
                pass
            else:
                error_handle(msg="mode syntax error")
        elif state == 4:
            pass
        else:
            error_handle(msg="state error")
    if state == 2:
        return "command"
    elif state == 3 or state == 1:
        return "mode"
    elif state == 4:
        return "param"
    else:
        error_handle(msg="fail to find type")


def lookup_analysis(table, state, sym):
    global analysis
    try:
        res = analysis["{},{},{}".format(table, state, sym)]
    except KeyError:
        res = ("syntax error", -1)
        error_handle(errcode=error_dict["<syntax error>"],
                     msg="语法错误: \n    参考语法: python main.py [--command] [-mode] [param] ...")
    return res


def shift(state, sym):
    global state_stack
    global sym_stack
    state_stack.append(state)
    sym_stack.append(sym)


def reduce(num):
    global grammar
    global state_stack
    global sym_stack
    gram = grammar[num].split(" ->")
    s = 0
    for i in range(len(gram[1])):
        if s == 0 and gram[1][i] != " ":
            s = 1
            state_stack.pop()
            sym_stack.pop()
        elif s == 1 and gram[1][i] == " ":
            s = 0
    sym_stack.append(gram[0])


def goto():
    global analysis
    global state_stack
    global sym_stack
    gt = lookup_analysis("goto", state_stack[-1:][0], sym_stack[-1:][0])
    state_stack.append(gt[1])


def accept():
    pass


# 语法分析
def argv_analyse(argv):
    global state_stack
    global sym_stack
    global analysis
    analysis_init()
    grammar_init()
    stack_init()
    command = ""
    mode = set()
    params = []
    for i in range(1, len(argv) + 1):
        if i == len(argv):
            tk = "$"
        else:
            tk = get_argv_token(argv[i])
            if tk == "command":
                command = argv[i][2:]
            elif tk == "mode":
                for j in range(1, len(argv[i])):
                    mode.add(argv[i][j])
            elif tk == "param":
                params.append(argv[i])
        act = lookup_analysis("action", state_stack[-1:][0], tk)
        if act[0] == "shift":
            shift(act[1], tk)
        elif act[0] == "accept":
            accept()
        while act[0] == "reduce":
            reduce(act[1] - 1)
            goto()
            act = lookup_analysis("action", state_stack[-1:][0], tk)
            if act[0] == "accept":
                accept()
                break
    return command, mode, params


# global parameter
lr1_path = "LR1.csv"
grammar_path = "grammar.txt"
error_dict = {
    "<default error>": -1,
    -1: "<default error>",
    "<syntax error>": 1,
    1: "<syntax error>",
}
# table,state,sym -> (action, num)
analysis = dict()
grammar = [""]
state_stack = []
sym_stack = []

if __name__ == "__main__":
    argv_analyse(sys.argv)
