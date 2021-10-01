# TODO: 制作数据，存在redis里面。（慎重！执行此文件会清空redis所有带有pcr_strategies_前缀的关键词！）
# TODO: 目前是B面
import xlrd
import json

# 读取配置文件
configure_src = r'./configures.json'
file = open(configure_src, 'r', encoding='utf-8')
data_json = json.load(file)
print(data_json)
print(data_json['stage'])
print(data_json['ban_list'])

# 重要的参数
p_list = data_json['ban_list']
data_src = './stage_' + data_json['stage'] + '.xlsx'


# 筛掉没有的角色的函数
def is_princess_existing(p_l, vals):
    for princess in p_l:
        for i1 in range(2, 7):
            if vals[i1] == princess:
                return False
    return True


# 打开表格
data = xlrd.open_workbook(data_src)
table = data.sheet_by_index(0)
# 开始制作数据文件
dict_line = dict()
temp_dict = dict()
cnt = 0
for i in range(0, table.nrows):
    val = table.row_values(i)
    if val[0] == '' or val[2] == '':
        continue
    # 筛掉没有的角色
    if not is_princess_existing(p_list, val):
        continue
    # 制作数据
    if val[2] == 511.0:
        val[2] = '511'
    if val[3] == 511.0:
        val[3] = '511'
    if val[4] == 511.0:
        val[4] = '511'
    if val[5] == 511.0:
        val[5] = '511'
    if val[6] == 511.0:
        val[6] = '511'
    print(val)
    dict_line['king_name'] = val[0]
    dict_line['id'] = val[1]
    dict_line['princess_1'] = val[2]
    dict_line['princess_2'] = val[3]
    dict_line['princess_3'] = val[4]
    dict_line['princess_4'] = val[5]
    dict_line['princess_5'] = val[6]
    dict_line['damage'] = val[7]
    text_json = json.dumps(dict_line)
    redis_index = 'pcr_strategies_' + str(cnt)
    temp_dict[redis_index] = text_json
    dict_line.clear()
    cnt += 1
temp_json = json.dumps(temp_dict)
# 写入文件中
with open('data.json', 'w') as f:
    f.write(temp_json)
