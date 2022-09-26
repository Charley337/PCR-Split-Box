from typing import List
import sys
import pcrhelper as ph
from pcrhelper import Plan, Homeworks, DataHandler, sn2king, sys_print


# TODO：以下部分是交互界面的功能函数
def func_search(cmd, plans: List[Plan], hws: Homeworks):
    """从所有分刀方案中，搜索需要的boss组合（boss按从小到大的顺序）

    格式：search [boss1] [boss2] [boss3] [used1] [used2]

    例如：search 2 3 4 CT208 C409

    默认显示前五条，剩余部分保存至 search.txt 中"""
    log_path = "./search.txt"
    length = len(cmd)
    used = []
    if length >= 4:
        boss = [cmd[1], cmd[2], cmd[3]]
        if length >= 5:
            used = cmd[4:]
        with open(log_path, "w", encoding="UTF-8") as fp:
            cnt = 0
            for plan in plans:
                if boss == [sn2king(plan.h1.sn)[1], sn2king(plan.h2.sn)[1], sn2king(plan.h3.sn)[1]]:
                    flag = True
                    for u in used:
                        flag = flag and (u in plan.sn)
                        if flag is False:
                            break
                    if flag:
                        plan_txt = "{}:   damage: {}, score: {}\n[{}], borrow: {}\n{}\nv1: {}\nv2: {}\nv3: {}\n".format(
                            cnt + 1, plan.damage, plan.score, plan.sn, plan.borrow, plan.names, plan.h1.video,
                            plan.h2.video, plan.h3.video)
                        fp.write(plan_txt + "\n")
                        if cnt < 5:
                            sys_print(plan_txt)
                        cnt += 1
    else:
        sys_print("Invalid params.")


def func_exit(cmd, plans: List[Plan], hws: Homeworks):
    """退出"""
    exit(0)


def func_show(cmd, plans: List[Plan], hws: Homeworks):
    """显示 plans 内容，默认显示10条

    格式：show [right] 或 show [left] [right]

    例如：show 10、show 5 20"""
    length = len(cmd)
    left = 0
    right = 10
    if length == 2:
        right = int(cmd[1])
    if length == 3:
        left = int(cmd[1])
        right = int(cmd[2])
    for i in range(left, right):
        sys_print("No.{}: damage: {}, score: {}, sn: [{}], borrow: {}\nnames: {}"
                  .format(i+1, plans[i].damage, plans[i].score, plans[i].sn, plans[i].borrow, plans[i].names))


def func_banlist(cmd, plans: List[Plan], hws: Homeworks):
    """显示 ban list"""
    sys_print(ph.ban_list)


def func_lacklist(cmd, plans: List[Plan], hws: Homeworks):
    """显示 ban list"""
    sys_print(ph.lack_list)


def func_saveplans(cmd, plans: List[Plan], hws: Homeworks):
    """保存 plans"""
    plans_path = "./plans.txt"
    length = len(plans)
    sys_print("There are {} plans, are you sure you want to save? (very large)".format(length))
    op = input("(Y/N): ")
    if op == "Y" or op == "y":
        with open(plans_path, "w", encoding="UTF-8") as fp:
            for i in range(length):
                fp.write("No.{}:   damage: {}, score: {}\n[{}],  borrow: {}\n{}\nvideo1: {}\nvideo2: {}\nvideo3: {}\n\n"
                         .format(i+1, plans[i].damage, plans[i].score, plans[i].sn, plans[i].borrow, plans[i].names,
                                 plans[i].h1.video, plans[i].h2.video, plans[i].h3.video))
    else:
        sys_print("Stop.")


def func_savehws(cmd, plans: List[Plan], hws: Homeworks):
    """保存 homeworks"""
    hws_path = "./homeworks.txt"
    length = len(hws.hws)
    with open(hws_path, "w", encoding="UTF-8") as fp:
        for i in range(length):
            fp.write("No.{}:  sn: {}, damage: {}, auto: {}, remain: {}, names: {}\nvideo: {}\n\n"
                     .format(i+1, hws.hws[i].sn, hws.hws[i].damage, hws.hws[i].auto, hws.hws[i].remain,
                             hws.hws[i].names, hws.hws[i].video))


def main():
    """程序入口 main 函数"""
    # 初始化 init
    functions = {"search": func_search,                 # 交互界面的函数功能表
                 "exit": func_exit,
                 "quit": func_exit,
                 "show": func_show,
                 "banlist": func_banlist,
                 "lacklist": func_lacklist,
                 "saveplans": func_saveplans,
                 "savehws": func_savehws,
                 }
    data_handler = DataHandler()  # 获取格式化的作业数据
    sys_len = len(sys.argv)

    sys_print("Get homeworks...")
    homeworks = data_handler.get_hws_from_data_files(mode=(sys.argv[3] if sys_len >= 4 else "auto"))

    sys_print("Analysing...")
    plans = homeworks.get_plans_auto(stage=("C" if sys_len < 2 else sys.argv[1]),
                                     sort_key=("score" if sys_len < 3 else sys.argv[2]),
                                     reverse=True)

    sys_print('Welcome! If you want to exit, please input "exit" or "quit".')
    while True:
        cmd = input("input: ")
        cmd = cmd.split(" ")
        try:
            functions[cmd[0]](cmd, plans, homeworks)
        except KeyError:
            sys_print('No such command "{}". Try:'.format(cmd[0]))
            for index in functions:
                print('            "{}"'.format(index))


if __name__ == "__main__":
    main()
