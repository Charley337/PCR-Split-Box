# TODO: 分析数据，生成out文件
# TODO: 目前是C面，生成out_c_2.txt
import redis
import json

# 重要参数
p_list = ['圣锤', '情病', '流夏', '春猫']
file_src = r'./out_2.txt'

conn = redis.Redis()


def get_multiplying_power(val):
    if val == 'A1':
        return 1.0
    elif val == 'A2':
        return 1.0
    elif val == 'A3':
        return 1.3
    elif val == 'A4':
        return 1.3
    elif val == 'A5':
        return 1.5
    elif val == 'B1':
        return 1.4
    elif val == 'B2':
        return 1.4
    elif val == 'B3':
        return 1.8
    elif val == 'B4':
        return 1.8
    elif val == 'B5':
        return 2.0
    elif val == 'C1':
        return 2.0
    elif val == 'C2':
        return 2.0
    elif val == 'C3':
        return 2.5
    elif val == 'C4':
        return 2.5
    elif val == 'C5':
        return 3.0
    else:
        return -10.0


def get_strategies():
    # 计算所有三刀并按伤害降序排序
    all_strategies = []
    prefix = 'pcr_strategies_'
    cnt = 0
    redis_index = prefix + str(cnt)
    content = conn.get(redis_index)
    # 获取所有刀的数据，得到一个列表
    while content is not None:
        dict_line = json.loads(content.decode('utf-8'))
        all_strategies.append(dict_line)
        # 依次递推
        cnt += 1
        redis_index = prefix + str(cnt)
        content = conn.get(redis_index)
    print(all_strategies)
    # 根据列表信息排刀
    # 三重循环，复杂度为O(n^3)
    all_feasible = []
    set_princess = set()
    for i in range(0, len(all_strategies)):
        # 制作公主集合，最后判断元素个数是否大于等于4 （这好像是废话）
        set_princess = set()
        set_princess.add(all_strategies[i]['princess_1'])
        set_princess.add(all_strategies[i]['princess_2'])
        set_princess.add(all_strategies[i]['princess_3'])
        set_princess.add(all_strategies[i]['princess_4'])
        set_princess.add(all_strategies[i]['princess_5'])
        set_princess_i = set()
        set_princess_i = set_princess.copy()
        for j in range(i + 1, len(all_strategies)):
            # 制作公主集合，最后判断元素个数是否大于等于8
            set_princess = set_princess_i.copy()
            set_princess.add(all_strategies[j]['princess_1'])
            set_princess.add(all_strategies[j]['princess_2'])
            set_princess.add(all_strategies[j]['princess_3'])
            set_princess.add(all_strategies[j]['princess_4'])
            set_princess.add(all_strategies[j]['princess_5'])
            if len(set_princess) < 8:
                continue
            set_princess_j = set()
            set_princess_j = set_princess.copy()
            for k in range(j + 1, len(all_strategies)):
                # 先判断元素个数是否大于等于12
                set_princess = set_princess_j.copy()
                set_princess.add(all_strategies[k]['princess_1'])
                set_princess.add(all_strategies[k]['princess_2'])
                set_princess.add(all_strategies[k]['princess_3'])
                set_princess.add(all_strategies[k]['princess_4'])
                set_princess.add(all_strategies[k]['princess_5'])
                if len(set_princess) < 12:
                    continue
                # 再判断第一刀和第三刀是否兼容
                set_princess = set_princess_i.copy()
                set_princess.add(all_strategies[k]['princess_1'])
                set_princess.add(all_strategies[k]['princess_2'])
                set_princess.add(all_strategies[k]['princess_3'])
                set_princess.add(all_strategies[k]['princess_4'])
                set_princess.add(all_strategies[k]['princess_5'])
                if len(set_princess) < 8:
                    continue
                # 最后判断第二刀和第三刀是否兼容
                set_princess = set()
                set_princess.add(all_strategies[j]['princess_1'])
                set_princess.add(all_strategies[j]['princess_2'])
                set_princess.add(all_strategies[j]['princess_3'])
                set_princess.add(all_strategies[j]['princess_4'])
                set_princess.add(all_strategies[j]['princess_5'])
                set_princess.add(all_strategies[k]['princess_1'])
                set_princess.add(all_strategies[k]['princess_2'])
                set_princess.add(all_strategies[k]['princess_3'])
                set_princess.add(all_strategies[k]['princess_4'])
                set_princess.add(all_strategies[k]['princess_5'])
                if len(set_princess) < 8:
                    continue
                # 到此为止说明三刀都兼容
                print('yes' + ' i=', i, ' j=', j, ' k=', k)
                # 计算毛分
                score = int(float(all_strategies[i]['damage'][:-1]) * float(get_multiplying_power(all_strategies[i]['king_name'])))
                score += int(float(all_strategies[j]['damage'][:-1]) * float(get_multiplying_power(all_strategies[j]['king_name'])))
                score += int(float(all_strategies[k]['damage'][:-1]) * float(get_multiplying_power(all_strategies[k]['king_name'])))
                dict_res_line = dict()
                dict_res_line['first_team'] = all_strategies[i].copy()
                dict_res_line['second_team'] = all_strategies[j].copy()
                dict_res_line['third_team'] = all_strategies[k].copy()
                dict_res_line['score'] = score
                all_feasible.append(dict_res_line)
    # 此时得到all_feasible列表为所有可行组合（乱序）
    # 接下来开始排序
    print('开始排序')
    print('all_feasible:', len(all_feasible))
    for i in range(0, len(all_feasible)):
        max_score = all_feasible[i]['score']
        max_loc = i
        for j in range(i + 1, len(all_feasible)):
            if max_score < all_feasible[j]['score']:
                max_score = all_feasible[j]['score']
                max_loc = j
        if max_loc != i:
            temp = all_feasible[i]
            all_feasible[i] = all_feasible[max_loc]
            all_feasible[max_loc] = temp
        print('i=', i, ' finish')
    print('排序结束')
    dict_res = dict()
    # 取全部
    dict_res['number'] = len(all_feasible)
    dict_res['best_feasible'] = all_feasible
    return dict_res


file = open(file_src, 'w')
dict_out = get_strategies()
if len(p_list) != 0:
    file.write('筛掉了含有')
    file.write(p_list[0])
    for i in range(1, len(p_list)):
        file.write('，')
        file.write(p_list[i])
    file.write('的刀\n')
file.write('总共有：' + str(dict_out['number']) + '种方案，按毛分从高到低排序。\n')
for i in range(0, dict_out['number']):
    file.write('毛分：' + str(dict_out['best_feasible'][i]['score']) + 'w  i=' + str(i + 1) + '\n')
    file.write('第一刀：编号：' + dict_out['best_feasible'][i]['first_team']['id'] + '  BOSS：' + dict_out['best_feasible'][i]['first_team']['king_name'] + '  阵容：' + str(dict_out['best_feasible'][i]['first_team']['princess_1']) + '，' + str(dict_out['best_feasible'][i]['first_team']['princess_2']) + '，' + str(dict_out['best_feasible'][i]['first_team']['princess_3']) + '，' + str(dict_out['best_feasible'][i]['first_team']['princess_4']) + '，' + str(dict_out['best_feasible'][i]['first_team']['princess_5']) + '  伤害：' + dict_out['best_feasible'][i]['first_team']['damage'] + '\n')
    file.write('第二刀：编号：' + dict_out['best_feasible'][i]['second_team']['id'] + '  BOSS：' + dict_out['best_feasible'][i]['second_team']['king_name'] + '  阵容：' + str(dict_out['best_feasible'][i]['second_team']['princess_1']) + '，' + str(dict_out['best_feasible'][i]['second_team']['princess_2']) + '，' + str(dict_out['best_feasible'][i]['second_team']['princess_3']) + '，' + str(dict_out['best_feasible'][i]['second_team']['princess_4']) + '，' + str(dict_out['best_feasible'][i]['second_team']['princess_5']) + '  伤害：' + dict_out['best_feasible'][i]['second_team']['damage'] + '\n')
    file.write('第三刀：编号：' + dict_out['best_feasible'][i]['third_team']['id'] + '  BOSS：' + dict_out['best_feasible'][i]['third_team']['king_name'] + '  阵容：' + str(dict_out['best_feasible'][i]['third_team']['princess_1']) + '，' + str(dict_out['best_feasible'][i]['third_team']['princess_2']) + '，' + str(dict_out['best_feasible'][i]['third_team']['princess_3']) + '，' + str(dict_out['best_feasible'][i]['third_team']['princess_4']) + '，' + str(dict_out['best_feasible'][i]['third_team']['princess_5']) + '  伤害：' + dict_out['best_feasible'][i]['third_team']['damage'] + '\n')
    print('写好一组 i=', i)
file.close()
print('写入完毕，关闭文件，程序结束')
