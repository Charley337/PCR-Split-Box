import json

# 读取配置文件
configure_src = r'./configures.json'
file = open(configure_src, 'r', encoding='utf-8')
data_json = json.load(file)
print(data_json)
print(data_json['stage'])
print(data_json['ban_list'])

# 文件路径
file_src = './out_' + data_json['stage'] + '.txt'
file_des = r'./search.txt'

# 输入筛选关键词
kings_list = [0, 0, 0]
kings_list[0] = input('请输入第一个BOSS：')
kings_list[1] = input('请输入第二个BOSS：')
kings_list[2] = input('请输入第三个BOSS：')
print(kings_list)

# 打开文件，读取掉标头
file = open(file_src, 'r')
print(file.readline())
print(file.readline())

# 筛选所需的变量
eligible_list = []
score = file.readline()


# 判断是否符合条件的函数
def is_eligible(f1, f2, f3):
    temp = []
    loc = f1.find("BOSS：")
    temp.append(f1[loc + 6])
    loc = f2.find("BOSS：")
    temp.append(f2[loc + 6])
    loc = f3.find("BOSS：")
    temp.append(f3[loc + 6])
    # print(temp)
    if temp == kings_list:
        return True
    else:
        return False


# 开始筛选循环
while score != "":
    # 读取三刀
    fight_1 = file.readline()
    fight_2 = file.readline()
    fight_3 = file.readline()
    # 判断是否符合要求
    if is_eligible(fight_1, fight_2, fight_3):
        eligible_list.append([score, fight_1, fight_2, fight_3])
    score = file.readline()
# print(eligible_list)

# 关闭文件
file.close()

# 写文件
file = open(file_des, 'w')
cnt = 0
for item in eligible_list:
    file.write(item[0])
    file.write(item[1])
    file.write(item[2])
    file.write(item[3])
    cnt += 1
print("总共有", cnt, "个")
# 关闭文件
file.close()

# 程序结束
print('ending')