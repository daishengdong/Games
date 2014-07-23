# -*- coding: utf-8 -*-

import threading
import operator
import copy

# for global use
ret_x, ret_y = -1, -1
computer_played = False

def get_data():
    return computer_played, ret_x, ret_y

# 能成 5
SCORE1 = 100000
# 成活 4，双死 4，死 4 活 3
SCORE2 = 10000
# 双活 3
SCORE3 = 5000
# 死 3 活 3
SCORE4 = 1000
# 单死 4
SCORE5 = 500
# 单活 3
SCORE6 = 200
# 双活 2
SCORE7 = 100
# 单死 3
SCORE8 = 50
# 单活 2
SCORE9 = 10
# 单死 2
SCORE10 = 3

# 无穷大
INFINITE = 10000000

# 博弈树的搜索深度
# 决定了 AI 的智能程度
# 搜索深度越深效率越低
SEARCH_DEPTH = 2

# 保存搜索节点的盘面情况和盘面大小
this_bitset, this_count = None, 0

# 空闲的位置
def avaliable_position():
    global this_bitset
    for x in xrange(0, this_count + 1):
        for y in xrange(0, this_count + 1):
            if this_bitset[x][y] == 'o':
                yield x, y

# 获取当前盘面 横、纵、正斜、反斜 四个棋路上棋子的布局
def get_layout(is_computer = True):
    if is_computer:
        # 横
        # another cool: layout = map(lambda x: operator.concat(operator.concat('+', x), '+'), map(''.join, bitset))
        layout = map(lambda x: '+' + x + '+', map(''.join, this_bitset))
        # 纵
        # map(''.join, zip(*bitset) 是 bitset 的转置
        layout.extend(map(lambda x: '+' + x + '+', map(''.join, zip(*this_bitset))))
    else:
        layout = map(lambda x: '*' + x + '*', map(''.join, this_bitset))
        layout.extend(map(lambda x: '*' + x + '*', map(''.join, zip(*this_bitset))))
    # 正斜 \
    layout_point = []
    for y in xrange(this_count + 1):
        if this_count - y + 1 < 5:
            # 去除拐角四个绝对连不成五子的线（长度最多只有 4）
            continue
        layout_point.append([(0 + i, y + i) for i in xrange(-1, this_count - y + 2)])

    for x in xrange(1, this_count + 1):
        if this_count - x + 1 < 5:
            # 去除拐角四个绝对连不成五子的线（长度最多只有 4）
            continue
        layout_point.append([(x + i, 0 + i) for i in xrange(-1, this_count - x + 2)])
    # 反斜 /
    for y in xrange(this_count + 1):
        if y + 1 < 5:
            # 去除拐角四个绝对连不成五子的线（长度最多只有 4）
            continue
        layout_point.append([(0 + i, y - i) for i in xrange(-1, y + 2)])

    for x in xrange(1, this_count + 1):
        if this_count - x + 1 < 5:
            # 去除拐角四个绝对连不成五子的线（长度最多只有 4）
            continue
        layout_point.append([(x + i, this_count - i) for i in xrange(-1, this_count - x + 2)])

    # * 表示计算机的棋子(白棋)
    # + 表示玩家的棋子(黑棋)
    # o 表示空白位
    # 其中，当在计算计算机的棋子布局时，边界也被表示为 +
    # 反之，在计算玩家的棋子布局时，边界被表示为 *
    # 这是因为，对方的棋子和边界都是表示阻隔，没必要区分
    if is_computer:
        # 获取电脑的棋子布局情况
        layout.extend(map(lambda points: ''.join(map(lambda (x, y): '+' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], points)), layout_point))
    else:
        # 获取玩家的棋子布局情况
        layout.extend(map(lambda points: ''.join(map(lambda (x, y): '*' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], points)), layout_point))
    return layout

# 某一条棋路布局的情况
def get_credential(layout, is_computer = True):
    credential = [False for _ in xrange(7)]
    if is_computer:
        if '*****' in layout:
            # 成 5
            credential[0] = True
        if 'o****o' in layout:
            # 活 4
            credential[1] = True
        if '+****o' in layout or 'o****+' in layout:
            # 死 4
            credential[2] = True
        if 'o***o' in layout:
            # 活 3
            credential[3] = True
        if '+***oo' in layout or 'oo***+' in layout:
            # 死 3
            credential[4] = True
        if 'o**oo' in layout or 'oo**o' in layout:
            # 活 2
            credential[5] = True
        if '+**ooo' in layout or 'ooo**+' in layout:
            # 死 2
            credential[6] = True
    else:
        if '+++++' in layout:
            # 成 5
            credential[0] = True
        if 'o++++o' in layout:
            # 活 4
            credential[1] = True
        if '*++++o' in layout or 'o++++*' in layout:
            # 死 4
            credential[2] = True
        if 'o+++o' in layout:
            # 活 3
            credential[3] = True
        if '*+++oo' in layout or 'oo+++*' in layout:
            # 死 3
            credential[4] = True
        if 'o++oo' in layout or 'oo++o' in layout:
            # 活 2
            credential[5] = True
        if '*++ooo' in layout or 'ooo++*' in layout:
            # 死 2
            credential[6] = True
    return credential

# 对当前盘面评分
def evalue():
    # 行、列、对角线上
    # 计算机得分 - 玩家得分
    score = 0
    # 计算机的得分
    credential_matrix = map(get_credential, get_layout())
    # credential_matrix 的转置矩阵
    tran_credential_matrix = zip(*credential_matrix)
    # 0       1       2       3       4       5       6
    # F_1     A4_1    D4_1    A3_1    D3_1    A2_1    D2_1

    while True:
        # 成 5
        if reduce(operator.ior, tran_credential_matrix[0]):
            score += SCORE1
            break

        # 活 4、双死 4、死 4 活 3
        if reduce(operator.ior, tran_credential_matrix[1]) \
                or tran_credential_matrix[2].count(True) >= 2 \
                or (reduce(operator.ior, tran_credential_matrix[2]) and reduce(operator.ior, tran_credential_matrix[3])):
            score += SCORE2
            break

        # 双活 3
        if tran_credential_matrix[3].count(True) >= 2:
            score += SCORE3
            break

        # 死 3 活 3
        if reduce(operator.ior, tran_credential_matrix[3]) and reduce(operator.ior, tran_credential_matrix[4]):
            score += SCORE4
            break

        # 单死 4
        if tran_credential_matrix[2].count(True) == 1:
            score += SCORE5
            break

        # 单活 3
        if tran_credential_matrix[3].count(True) == 1:
            score += SCORE6
            break

        # 双活 2
        if tran_credential_matrix[5].count(True) >= 2:
            score += SCORE7
            break

        # 单死 3
        if tran_credential_matrix[4].count(True) == 1:
            score += SCORE8
            break

        # 单活 2
        if tran_credential_matrix[5].count(True) == 1:
            score += SCORE9
            break

        # 单死 2
        if tran_credential_matrix[6].count(True) == 1:
            score += SCORE10
            break

        break

    # 玩家的得分
    credential_matrix = map(lambda x: get_credential(x, False), get_layout(False))
    # credential_matrix 的转置矩阵
    tran_credential_matrix = zip(*credential_matrix)

    while True:
        # 成 5
        if reduce(operator.ior, tran_credential_matrix[0]):
            score -= SCORE1
            break

        # 活 4、双死 4、死 4 活 3
        if reduce(operator.ior, tran_credential_matrix[1]) \
                or tran_credential_matrix[2].count(True) >= 2 \
                or (reduce(operator.ior, tran_credential_matrix[2]) and reduce(operator.ior, tran_credential_matrix[3])):
            score -= SCORE2
            break

        # 双活 3
        if tran_credential_matrix[3].count(True) >= 2:
            score -= SCORE3
            break

        # 死 3 活 3
        if reduce(operator.ior, tran_credential_matrix[3]) and reduce(operator.ior, tran_credential_matrix[4]):
            score -= SCORE4
            break

        # 单死 4
        if tran_credential_matrix[2].count(True) == 1:
            score -= SCORE5
            break

        # 单活 3
        if tran_credential_matrix[3].count(True) == 1:
            score -= SCORE6
            break

        # 双活 2
        if tran_credential_matrix[5].count(True) >= 2:
            score -= SCORE7
            break

        # 单死 3
        if tran_credential_matrix[4].count(True) == 1:
            score -= SCORE8
            break

        # 单活 2
        if tran_credential_matrix[5].count(True) == 1:
            score -= SCORE9
            break

        # 单死 2
        if tran_credential_matrix[6].count(True) == 1:
            score -= SCORE10
            break

        break

    # now, life is better...
    return score

# alpha 表示电脑目前能达到的最大分数, alpha 要求越大越好
# beta 表示人目前能达到的最大分数，beta 要求越小越好
def Max(alpha, beta, depth):
    # 电脑的试探，求极大子节点
    global this_bitset
    if depth == SEARCH_DEPTH:
        return evalue()
    for x, y in avaliable_position():
        # 尝试在 (x, y) 处下白子
        this_bitset[x][y] = '*'
        # alpha = max(alpha, Min(alpha, beta, depth + 1))
        val = Min(alpha, beta, depth + 1)
        # 撤销
        this_bitset[x][y] = 'o'

        # 当前层需要求的是极大值
        if val > alpha:
            # 找到一个极大值
            global ret_x, ret_y
            ret_x, ret_y = x, y
            alpha = val
        # beta 剪枝
        if val >= beta:
            return beta
    return alpha

def Min(alpha, beta, depth):
    # 假设人的试探，求极小子节点
    if depth == SEARCH_DEPTH:
        a = evalue()
        return evalue()
    for x, y in avaliable_position():
        # 尝试在 (x, y) 处下黑子
        this_bitset[x][y] = '+'
        # beta = min(beta, Max(alpha, beta, depth + 1))
        val = Max(alpha, beta, depth + 1)
        # 撤销
        this_bitset[x][y] = 'o'

        # 当前层需要求的是极小值
        if val < beta:
            beta = val
        # alpha 剪枝
        if val <= alpha:
            return alpha
    return beta

class searchThread(threading.Thread):  
    def __init__(self, bitset, count):
        threading.Thread.__init__(self)  
        global this_bitset, this_count
        this_bitset = copy.deepcopy(bitset)
        this_count = count
          
    def run(self):  
        global computer_played
        computer_played = False
        alpha, beta = -INFINITE, INFINITE
        Max(alpha, beta, 0)
        computer_played = True
