from typing import List
import os
import json
import requests
import time

# boss 毛分倍率
score_rate = {"A1": 1.2, "A2": 1.2, "A3": 1.3, "A4": 1.4, "A5": 1.5,
              "B1": 1.6, "B2": 1.6, "B3": 1.8, "B4": 1.9, "B5": 2.0,
              "C1": 2.0, "C2": 2.0, "C3": 2.4, "C4": 2.4, "C5": 2.6,
              "D1": 3.5, "D2": 3.5, "D3": 3.7, "D4": 3.8, "D5": 4.0}
sys_name = "Ikaros"
config = dict()
ban_list = []
lack_list = []


class Homework:
    """单个作业"""
    def __init__(self, name1, name2, name3, name4, name5, auto, damage, remain, sn, video=None):
        self.names = [name1, name2, name3, name4, name5]
        self.auto = int(auto)
        self.damage = int(damage)
        self.remain = int(remain)
        self.sn = sn
        self.video = [] if video is None else video


class Plan:
    """单个分刀方案"""
    def __init__(self, h1: Homework, h2: Homework, h3: Homework, borrow):
        self.h1 = h1
        self.h2 = h2
        self.h3 = h3
        self.borrow = borrow
        self.damage = self.h1.damage + self.h2.damage + self.h3.damage
        self.sn = "{}, {}, {}".format(self.h1.sn, self.h2.sn, self.h3.sn)
        self.names = "{}, {}, {}".format(self.h1.names, self.h2.names, self.h3.names)
        self.score = score_rate[sn2king(self.h1.sn)] * self.h1.damage
        self.score += score_rate[sn2king(self.h2.sn)] * self.h2.damage
        self.score += score_rate[sn2king(self.h3.sn)] * self.h3.damage


class Homeworks:
    """全部作业"""
    def __init__(self, homework_list: List[Homework]):
        self.hws = homework_list
        self.hws.sort(key=lambda x: x.sn, reverse=False)
        self.num = len(self.hws)
        self.ns1 = 0
        self.ns2 = 0
        self.ns3 = 0
        self.ns4 = 0
        for hw in self.hws:
            if hw.sn[0] == "A":
                self.ns1 += 1
            elif hw.sn[0] == "B":
                self.ns2 += 1
            elif hw.sn[0] == "C":
                self.ns3 += 1
            else:
                self.ns4 += 1
        self.get_stage = {"A": self.get_stage_a, "B": self.get_stage_b, "C": self.get_stage_c, "D": self.get_stage_d}

    def get_stage_a(self):
        """获取 A 面所有作业的切片
        :return: A 面的所有作业（不是分刀方案哦）"""
        return self.hws[:self.ns1]

    def get_stage_b(self):
        return self.hws[self.ns1:self.ns1+self.ns2]

    def get_stage_c(self):
        return self.hws[self.ns1+self.ns2:self.ns1+self.ns2+self.ns3]

    def get_stage_d(self):
        return self.hws[self.ns1+self.ns2+self.ns3:]

    def get_plans(self, stage="C", sort_key="damage", reverse=False):
        """
        计算所有分刀方案（所有刀）
        :param stage: 阶段
        :param sort_key: 排序依据
        :param reverse: 是否降序
        :return: 所有分刀方案
        """
        hws = self.get_stage[stage]()
        plans = []
        length = len(hws)
        for i in range(0, length):
            for j in range(i + 1, length):
                for k in range(j + 1, length):
                    if hws[i].remain+hws[j].remain+hws[k].remain == 0:
                        boolean, borrow = feasible3(hws[i], hws[j], hws[k])
                        if boolean:
                            plans.append(Plan(hws[i], hws[j], hws[k], borrow))
        if sort_key == "score":
            plans.sort(key=lambda x: x.score, reverse=reverse)
        else:
            plans.sort(key=lambda x: x.damage, reverse=reverse)
        return plans

    def get_plans_auto(self, stage="C", sort_key="damage", reverse=False):
        """
        计算所有 auto 刀的分刀方案（仅auto）
        :param stage: 阶段，默认 C 面
        :param sort_key: 排序的依据，默认总伤害
        :param reverse: 是否降序
        :return: 所有 auto 刀的方案
        """
        hws = self.get_stage[stage]()
        plans = []
        length = len(hws)
        for i in range(0, length):
            for j in range(i + 1, length):
                for k in range(j + 1, length):
                    if hws[i].auto*hws[j].auto*hws[k].auto == 1 and hws[i].remain+hws[j].remain+hws[k].remain == 0:
                        boolean, borrow = feasible3(hws[i], hws[j], hws[k])
                        if boolean:
                            plans.append(Plan(hws[i], hws[j], hws[k], borrow))
        if sort_key == "score":
            plans.sort(key=lambda x: x.score, reverse=reverse)
        else:
            plans.sort(key=lambda x: x.damage, reverse=reverse)
        return plans


class DataHandler:
    """用于获取、处理原始数据，并输出Homeworks对象管理的格式化作业数据"""
    def __init__(self):
        self.data_path = "./data.json"
        self.icon_path = "./icon.json"
        self.id2name_path = "./id2name.json"
        self.html_path = "./gzlj.html"
        self.base_url = "https://www.caimogu.cc"
        self.icon_url = "/gzlj/data/icon?date=&lang=zh-cn"
        self.data_url = "/gzlj/data?date=&lang=zh-ch"
        self.headers = {
            "authority": "www.caimogu.cc",
            "method": "GET",
            "path": "/gzlj/data?date=&lang=zh-cn",
            "scheme": "https",
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "zh-CN,zh;q=0.9",
            "cookie": "",
            "referer": "https://www.caimogu.cc/gzlj.html",
            "sec-ch-ua": '"Chromium";v="104", " Not A;Brand";v="99", "Google Chrome";v="104"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36",
            "x-requested-with": "XMLHttpRequest"
        }

    def request_data_and_save_into_files(self):
        """使用request请求数据接口，并将数据保存在文件中"""
        sys_print("try to request data from {}/".format(self.base_url))
        icon = requests.get(self.base_url + self.icon_url, headers=self.headers)
        sys_print("icon status: {}".format(icon.status_code))
        icon = json.loads(icon.text)
        with open(self.icon_path, "w", encoding="UTF-8") as fp:
            json.dump(icon, fp)
        sys_print("wait 1 sec...")
        time.sleep(1)
        data = requests.get(self.base_url + self.data_url, headers=self.headers)
        sys_print("data status: {}".format(data.status_code))
        data = json.loads(data.text)
        with open(self.data_path, "w", encoding="UTF-8") as fp:
            json.dump(data, fp)
        id2name = dict()
        length_i = len(icon["data"])
        for i in range(length_i):
            length_j = len(icon["data"][i])
            for j in range(length_j):
                id2name[icon["data"][i][j]["id"]] = icon["data"][i][j]["iconValue"]
        with open(self.id2name_path, "w", encoding="UTF-8") as fp:
            json.dump(id2name, fp)

    def get_hws_from_data_files(self, mode="auto") -> Homeworks:
        """通过数据接口收到的数据获取作业数据"""
        if mode not in ["always", "auto", "never"]:
            raise ValueError('There is no mode called "{}". Valid mode: ["always", "auto", "never"]'.format(mode))
        if mode == "always":
            self.request_data_and_save_into_files()
        elif mode == "auto":
            if os.path.isfile(self.data_path) is False or os.path.isfile(self.id2name_path) is False:
                self.request_data_and_save_into_files()
        elif mode == "never":
            if os.path.isfile(self.data_path) is False or os.path.isfile(self.id2name_path) is False:
                return None
        else:
            raise Exception("unknown error!!!")
        with open(self.data_path, "r", encoding="UTF-8") as fp:
            data = json.load(fp)
        with open(self.id2name_path, "r", encoding="UTF-8") as fp:
            id2name = json.load(fp)
        hws = []
        sn_set = set()
        length_i = len(data["data"])
        for i in range(length_i):
            length_j = len(data["data"][i]["homework"])
            for j in range(length_j):
                sn = data["data"][i]["homework"][j]["sn"]
                if sn in sn_set:
                    continue
                sn_set.add(sn)  # 遇到没见过的sn将其加入set中
                length_k = len(data["data"][i]["homework"][j]["unit"])
                for k in range(length_k):
                    data["data"][i]["homework"][j]["unit"][k] = id2name[str(data["data"][i]["homework"][j]["unit"][k])]
                names = data["data"][i]["homework"][j]["unit"]
                if (names[0] in ban_list) or (names[1] in ban_list) or (names[2] in ban_list) or (
                        names[3] in ban_list) or (names[4] in ban_list):
                    continue
                damage = data["data"][i]["homework"][j]["damage"]
                auto = data["data"][i]["homework"][j]["auto"]
                remain = data["data"][i]["homework"][j]["remain"]
                video = data["data"][i]["homework"][j]["video"]
                hws.append(Homework(names[0], names[1], names[2], names[3], names[4], auto, damage, remain, sn, video))
        hws = Homeworks(hws)
        return hws

    def get_hws_from_html_file(self):
        """
        需要先将网页 https://www.caimogu.cc/gzlj.html 保存到 gzlj.html 文件中
        拆分html数据，格式化成作业（class Homework）的形式，输出全部作业（class Homeworks）
        :return: Homeworks
        """
        hws = []
        with open(self.html_path, "r", encoding="UTF-8") as fp:
            data = fp.read()
        data = data.split('class="homework-wrap homework"')[1:]
        length = len(data)
        for i in range(length):
            data[i] = data[i].split(">")[0]
            name1 = data[i].split('data-param-name1="')[1].split('"')[0]
            name2 = data[i].split('data-param-name2="')[1].split('"')[0]
            name3 = data[i].split('data-param-name3="')[1].split('"')[0]
            name4 = data[i].split('data-param-name4="')[1].split('"')[0]
            name5 = data[i].split('data-param-name5="')[1].split('"')[0]
            if (name1 in ban_list) or (name2 in ban_list) or (name3 in ban_list) or (name4 in ban_list) or (
                    name5 in ban_list):
                continue
            auto = data[i].split('data-param-auto="')[1].split('"')[0]
            damage = data[i].split('data-param-damage="')[1].split('"')[0]
            remain = data[i].split('data-param-remain="')[1].split('"')[0]
            sn = data[i].split('data-param-sn="')[1].split('"')[0]
            hws.append(Homework(name1, name2, name3, name4, name5, auto, damage, remain, sn))
        hws = Homeworks(hws)
        return hws


def load_config():
    """
    config配置表（包含 ban list），config保存在全局变量中
    """
    global config
    global ban_list
    global lack_list
    config_path = "./config.json"
    if os.path.isfile(config_path) is False:
        config["ban_list"] = []
        config["lack_list"] = []
        with open(config_path, "w", encoding="UTF-8") as fp:
            json.dump(config, fp)
    else:
        with open(config_path, "r", encoding="UTF-8") as fp:
            config = json.load(fp)
    ban_list = config["ban_list"]
    lack_list = config["lack_list"]
    sys_print("ban list: {};  lack list: {}".format(ban_list, lack_list))


def sys_print(content):
    print("{}: {}".format(sys_name, content))


def sn2king(x):
    """
    从标号中提取出 boss 名。 例如 CT402 -> C4
    :param x: sn (e.g. CT302)
    :return: king (e.g. C3)
    """
    x1 = x[1]
    x2 = x[2]
    return x[0] + (x2 if (x1 == "T" or x1 == "W") else x1)


def feasible1(h: Homework):
    """在考虑缺少角色的情况下，判断一刀是否可行"""
    global lack_list
    name_set = set()
    for n in h.names:
        if n not in lack_list:
            name_set.add(n)
    length = len(name_set)
    if length < 4:
        return False
    else:
        return True


def feasible2(h1: Homework, h2: Homework):
    """判断两刀之间能否兼容"""
    global lack_list
    if feasible1(h1) and feasible1(h2):
        name_set = set()
        for n in h1.names:
            if n not in lack_list:
                name_set.add(n)
        for n in h2.names:
            if n not in lack_list:
                name_set.add(n)
        length = len(name_set)
        if length < 8:
            return False
        else:
            return True
    else:
        return False


def feasible3(h1: Homework, h2: Homework, h3: Homework):
    """判断三刀之间能否兼容（不考虑两两之间），并输出需要嫖的名单"""
    global lack_list
    if feasible2(h1, h2) and feasible2(h1, h3) and feasible2(h2, h3):
        name_set = set()
        borrow = []
        for n in h1.names:
            name_set.add(n)
        for n in h2.names:
            if n in name_set:
                borrow.append(n)
            else:
                name_set.add(n)
        for n in h3.names:
            if n in name_set:
                borrow.append(n)
            else:
                name_set.add(n)
        for n in name_set:
            if n in lack_list:
                borrow.append(n)
        length = len(borrow)
        if length > 3:
            return False, []
        else:
            return True, borrow
    else:
        return False, []


# 初始化，加载配置文件
load_config()
