# TODO: 优化了筛选算法，重构了分析部分
import utils
import json
import xlrd


def is_princess_banned(ban_list, table_row):
    for i in range(2, 7):
        if table_row[i] in ban_list:
            return True
    return False


def make_data():
    global config
    # 读取配置文件
    config = utils.check_config(config)
    # 重要参数
    ban_list = config["ban_list"]
    data_src = "./stage_{}.xlsx".format(config["stage"])
    # 打开表格
    table_file = xlrd.open_workbook(data_src)
    table = table_file.sheet_by_index(0)
    # 开始制作数据文件
    cnt = 0
    res_item = dict()
    res_data = dict()
    print("开始数据预处理")
    for i in range(0, table.nrows):
        table_row = table.row_values(i)
        if table_row[0] == '' or table_row[2] == '':
            continue
        # 筛掉禁用的角色
        if is_princess_banned(ban_list, table_row):
            continue
        # 制作数据
        for j in range(2, 7):
            if table_row[j] == 511.0:
                table_row[j] = "511"
        res_item["king_name"] = table_row[0]
        res_item["id"] = table_row[1]
        res_item["princess_1"] = table_row[2]
        res_item["princess_2"] = table_row[3]
        res_item["princess_3"] = table_row[4]
        res_item["princess_4"] = table_row[5]
        res_item["princess_5"] = table_row[6]
        res_item["damage"] = table_row[7]
        res_index = "pcr_strategies_{}".format(cnt)
        res_data[res_index] = json.dumps(res_item)
        res_item.clear()
        cnt += 1
    res_data = json.dumps(res_data)
    # 写入文件
    print("将预处理数据写入 ./temp/data.json 文件中")
    with open("./temp/data.json", "w") as file:
        file.write(res_data)


# 计算部分
def get_multiplying_power(boss):
    global multiplying_power
    try:
        return multiplying_power[boss]
    except:
        return -10.0


# 用来判断两刀之间是否兼容
def get_set_number(team1, team2, idx1, idx2):
    pri_set = set()
    for i in range(1, 6):
        if i != idx1:
            pri_set.add(team1["princess_{}".format(i)])
        if i != idx2:
            pri_set.add(team2["princess_{}".format(i)])
    return len(pri_set)


# 判断三刀是否兼容
def is_compatible(team1, team2, team3, miss_list):
    # 一刀里面只要有两个没有的角色就不行
    cnt1 = 0
    cnt2 = 0
    cnt3 = 0
    idx1 = 0
    idx2 = 0
    idx3 = 0
    for i in range(1, 6):
        if team1["princess_{}".format(i)] in miss_list:
            cnt1 += 1
            idx1 = i
            if cnt1 >= 2:
                return False
        if team2["princess_{}".format(i)] in miss_list:
            cnt2 += 1
            idx2 = i
            if cnt2 >= 2:
                return False
        if team3["princess_{}".format(i)] in miss_list:
            cnt3 += 1
            idx3 = i
            if cnt3 >= 2:
                return False
    princess_set = set()
    for i in range(1, 6):
        if i != idx1:
            princess_set.add(team1["princess_{}".format(i)])
        if i != idx2:
            princess_set.add(team2["princess_{}".format(i)])
        if i != idx3:
            princess_set.add(team3["princess_{}".format(i)])
    if len(princess_set) < 12:
        return False
    if get_set_number(team1, team2, idx1, idx2) < 8:
        return False
    if get_set_number(team2, team3, idx2, idx3) < 8:
        return False
    if get_set_number(team1, team3, idx1, idx3) < 8:
        return False
    return True


def get_strategies(data, miss_list):
    # 计算所有三刀并按伤害降序排序
    all_strategies = []
    cnt = 0
    index = "pcr_strategies_{}".format(cnt)
    try:
        item = data[index]
    except:
        item = None
    # 获取所有刀的数据，得到一个列表
    while item is not None:
        item = json.loads(item)
        all_strategies.append(item)
        # 依次递推
        cnt += 1
        index = "pcr_strategies_{}".format(cnt)
        try:
            item = data[index]
        except:
            item = None
    # 根据列表信息排刀
    # 三重循环，复杂度为O(n^3)
    result = dict()
    result["best_feasible"] = []
    print("开始筛选")
    for i in range(0, len(all_strategies)):
        for j in range(i + 1, len(all_strategies)):
            for k in range(j + 1, len(all_strategies)):
                if is_compatible(all_strategies[i], all_strategies[j], all_strategies[k], miss_list):
                    # 计算毛分
                    score = int(float(all_strategies[i]['damage'][:-1]) * float(
                        get_multiplying_power(all_strategies[i]['king_name'])))
                    score += int(float(all_strategies[j]['damage'][:-1]) * float(
                        get_multiplying_power(all_strategies[j]['king_name'])))
                    score += int(float(all_strategies[k]['damage'][:-1]) * float(
                        get_multiplying_power(all_strategies[k]['king_name'])))
                    one_feasible = dict()
                    one_feasible["first_team"] = all_strategies[i]
                    one_feasible["second_team"] = all_strategies[j]
                    one_feasible["third_team"] = all_strategies[k]
                    one_feasible["score"] = score
                    result["best_feasible"].append(one_feasible)
    # 开始排序
    print("开始排序，共有{}个排刀".format(len(result["best_feasible"])))
    result["best_feasible"].sort(key=lambda s: (s.get("score"), 0), reverse=True)
    result["number"] = len(result["best_feasible"])
    return result


def compute():
    global config
    # 读取配置文件
    config = utils.check_config(config)
    # 重要参数
    ban_list = config["ban_list"]
    miss_list = config["miss_list"]
    file_src = "./temp/out_{}.txt".format(config["stage"])
    # 加载预处理数据
    with open("./temp/data.json", "r") as file:
        data = json.load(file)
    data = get_strategies(data, miss_list)
    print("开始写入 {}".format(file_src))
    with open(file_src, "w") as file:
        if len(ban_list) != 0:
            file.write("筛掉了含有")
            file.write(ban_list[0])
            for i in range(1, len(ban_list)):
                file.write("，")
                file.write(ban_list[i])
            file.write("的刀\n")
        file.write("总共有：{}种方案，按毛分从高到低排序。\n".format(data["number"]))
        for i in range(0, data["number"]):
            file.write("毛分：{}w i={}\n".format(data["best_feasible"][i]["score"], i + 1))
            file.write("第一刀：编号：{}  BOSS：{}  阵容：{}，{}，{}，{}，{}  伤害：{}\n".format(
                data["best_feasible"][i]["first_team"]["id"],
                data["best_feasible"][i]["first_team"]["king_name"],
                data["best_feasible"][i]["first_team"]["princess_1"],
                data["best_feasible"][i]["first_team"]["princess_2"],
                data["best_feasible"][i]["first_team"]["princess_3"],
                data["best_feasible"][i]["first_team"]["princess_4"],
                data["best_feasible"][i]["first_team"]["princess_5"],
                data["best_feasible"][i]["first_team"]["damage"]
            ))
            file.write("第二刀：编号：{}  BOSS：{}  阵容：{}，{}，{}，{}，{}  伤害：{}\n".format(
                data["best_feasible"][i]["second_team"]["id"],
                data["best_feasible"][i]["second_team"]["king_name"],
                data["best_feasible"][i]["second_team"]["princess_1"],
                data["best_feasible"][i]["second_team"]["princess_2"],
                data["best_feasible"][i]["second_team"]["princess_3"],
                data["best_feasible"][i]["second_team"]["princess_4"],
                data["best_feasible"][i]["second_team"]["princess_5"],
                data["best_feasible"][i]["second_team"]["damage"]
            ))
            file.write("第三刀：编号：{}  BOSS：{}  阵容：{}，{}，{}，{}，{}  伤害：{}\n".format(
                data["best_feasible"][i]["third_team"]["id"],
                data["best_feasible"][i]["third_team"]["king_name"],
                data["best_feasible"][i]["third_team"]["princess_1"],
                data["best_feasible"][i]["third_team"]["princess_2"],
                data["best_feasible"][i]["third_team"]["princess_3"],
                data["best_feasible"][i]["third_team"]["princess_4"],
                data["best_feasible"][i]["third_team"]["princess_5"],
                data["best_feasible"][i]["third_team"]["damage"]
            ))
    print("写入完毕，程序结束")


def main():
    make_data()
    compute()
    return 0


config = dict()
multiplying_power = {
    "A1": 1.0,
    "A2": 1.0,
    "A3": 1.3,
    "A4": 1.3,
    "A5": 1.5,
    "B1": 1.4,
    "B2": 1.4,
    "B3": 1.8,
    "B4": 1.8,
    "B5": 2.0,
    "C1": 2.0,
    "C2": 2.0,
    "C3": 2.5,
    "C4": 2.5,
    "C5": 3.0
}

if __name__ == "__main__":
    exit(main())


