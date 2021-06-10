# TODO: 制作数据，存在redis里面。（慎重！执行此文件会清空redis所有带有pcr_strategies_前缀的关键词！）
# TODO: 目前是B面
import xlrd
import json
import redis

# 重要的参数
p_list = ['圣锤', '情病', '流夏', '春猫']
data_src = r'./stage_2.xlsx'


# 筛掉没有的角色的函数
def is_princess_existing(p_l, vals):
    for princess in p_l:
        for i1 in range(2, 7):
            if vals[i1] == princess:
                return False
    return True


# 打开redis
conn = redis.Redis()
# 清空带有pcr_strategies_前缀的关键词
list_keys = conn.keys('pcr_strategies_*')
for key in list_keys:
    print('del ' + key.decode('utf-8'))
    conn.delete(key)
print('redis清除完成')
# 打开表格
data = xlrd.open_workbook(data_src)
table = data.sheet_by_index(0)
# 开始制作数据文件
dict_line = dict()
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
    conn.set(redis_index, text_json)
    dict_line.clear()
    cnt += 1