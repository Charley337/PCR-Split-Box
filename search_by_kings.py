import sys
import json

# 开场白
print("beginning...")
print('============================================================================================================')
print('   _/  | \     _\_           ___       ___|___        /_____   _/ |-===-|     ________                       ')
print('   -|--|--    __ | __    \  _____       ==|==     __ /  | /   /|  ||-+-||      ____ |                       ')
print('   -|-  \/     / | \_   --| _| |__    __|===|__   \/   / \     |  /| |`||      |__| |                        ')
print('   \|   /\/  /  \|   \   |---------     |===|     /\  /   \_   | /   |   \__/      \|                       ')
print('============================================================================================================')

# 读取配置文件
configure_src = r'./configures.json'
file = open(configure_src, 'r', encoding='utf-8')
data_json = json.load(file)
print('配置文件数据：', data_json)
# print(data_json['stage'])
# print(data_json['ban_list'])

# 文件路径
file_src = './out_' + data_json['stage'] + '.txt'
file_des = r'./search.txt'

# 通过命令行输入参数
print(len(sys.argv))
if len(sys.argv) == 1:      # 如果等于1，那么启动提示输入参数
    # 输入筛选关键词
    kings_list = [0, 0, 0]
    kings_list[0] = input('请输入第一个BOSS：')
    kings_list[1] = input('请输入第二个BOSS：')
    kings_list[2] = input('请输入第三个BOSS：')
    print('BOSS组合：', kings_list)
    # 输入已经出过了什么刀
    done_set = set()
    done_num = input('请输入已经出过几刀(请按套路出牌，球球了: 0, 1, 2)：')
    done_num = int(done_num)
    if (done_num > 2) or (done_num < 0):
        done_num = 0
    for i in range(0, done_num):
        input_temp = input('请输入刀的标号（例如：B102，注意大小写）：')
        done_set.add(input_temp)
    print('已经出过的刀：', done_set)
else:       # 其余情况通过命令行传参
    # 筛选关键词
    kings_list = [0, 0, 0]
    kings_list[0] = sys.argv[1]
    kings_list[1] = sys.argv[2]
    kings_list[2] = sys.argv[3]
    print('BOSS组合：', kings_list)
    # 已经出过什么刀
    done_set = set()
    for i in range(4, len(sys.argv)):
        if i >= 6:
            print('输入错误，已经出过的刀最多为2个（出完了还来搜索作甚 TwT）')
            break
        done_set.add(sys.argv[i])
    print('已经出过的刀：', done_set)

# 打开文件，读取掉标头
file = open(file_src, 'r')
file.readline()
file.readline()

# 筛选所需的变量
eligible_list = []
score = file.readline()


# 判断是否符合条件的函数
def is_eligible(f1, f2, f3):
    temp = []
    temp_set = set()
    loc = f1.find("BOSS：")
    temp.append(f1[loc + 6])
    loc = f2.find("BOSS：")
    temp.append(f2[loc + 6])
    loc = f3.find("BOSS：")
    temp.append(f3[loc + 6])
    # print(temp)
    loc = f1.find("编号：")
    loc_2 = f1.find("BOSS：")
    temp_set.add(f1[loc + 3: loc_2 - 2])
    loc = f2.find("编号：")
    loc_2 = f2.find("BOSS：")
    temp_set.add(f2[loc + 3: loc_2 - 2])
    loc = f3.find("编号：")
    loc_2 = f3.find("BOSS：")
    temp_set.add(f3[loc + 3: loc_2 - 2])
    # print(temp_set)
    if temp == kings_list:
        if temp_set >= done_set:
            return True
        else:
            return False
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
print('============================================================================================================')
print("结果：筛选出", cnt, "个方案，保存在 search.txt 文件中")
# 关闭文件
file.close()

# 结果展示 至多3条
print('结果展示(至多3条)：')
file = open(file_des, 'r')
for i in range(0, 3):
    if i >= cnt:
        break
    print(i+1, ': ', file.readline()[:-1])
    print(file.readline()[:-1])
    print(file.readline()[:-1])
    print(file.readline()[:-1])
file.close()

# 程序结束
print('============================================================================================================')
print('ending')
