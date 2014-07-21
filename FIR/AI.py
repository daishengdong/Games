# -*- coding: utf-8 -*-
import threading

# for global use
ret_x, ret_y = -1, -1
computer_played = False

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
SEARCH_DEPTH = 3

this_bitset, this_count = None, 0
computer_points, player_points = [], []

def avaliable_position():
    global this_bitset
    for x in xrange(0, this_count + 1):
        for y in xrange(0, this_count + 1):
            if this_bitset[x][y] == 0:
                yield x, y

def get_layout((x, y), is_computer = True):
    # 横
    layout1 = [(x + i, y) for i in xrange(-4, 5)]
    # 纵
    layout2 = [(x, y + i) for i in xrange(-4, 5)]
    # 正斜 \
    layout3 = [(x + i, y + i) for i in xrange(-4, 5)]
    # 反斜 /
    layout4 = [(x - i, y + i) for i in xrange(-4, 5)]

    # * 表示计算机的棋子(白棋)
    # + 表示玩家的棋子(黑棋)
    # o 表示空白位
    # 其中，当在计算计算机的棋子布局时，边界也被表示为 +
    # 反之，在计算玩家的棋子布局时，边界被表示为 *
    # 这是因为，对方的棋子和边界都是表示阻隔，没必要区分
    if is_computer:
        # 获取电脑的棋子布局情况
        ret_layout1 = ''.join(map(lambda (x, y): '+' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], layout1))
        ret_layout2 = ''.join(map(lambda (x, y): '+' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], layout2))
        ret_layout3 = ''.join(map(lambda (x, y): '+' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], layout3))
        ret_layout4 = ''.join(map(lambda (x, y): '+' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], layout4))
    else:
        # 获取玩家的棋子布局情况
        ret_layout1 = ''.join(map(lambda (x, y): '*' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], layout1))
        ret_layout2 = ''.join(map(lambda (x, y): '*' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], layout2))
        ret_layout3 = ''.join(map(lambda (x, y): '*' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], layout3))
        ret_layout4 = ''.join(map(lambda (x, y): '*' if x < 0 or x > this_count or y < 0 or y > this_count else this_bitset[x][y], layout4))
    return ret_layout1, ret_layout2, ret_layout3, ret_layout4

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

def evalue():
    # 行、列、对角线上
    # 计算机得分 - 玩家得分
    score = 0
    five_cnt, dead_four_cnt, alive_four_cnt = 0, 0, 0
    dead_three_cnt, alive_three_cnt, dead_two_cnt, alive_two_cnt = 0, 0, 0, 0
    layout1, layout2, layout3, layout4 = None, None, None, None
    for (x, y) in computer_points:
        layout1, layout2, layout3, layout4 = get_layout()
        F_1, A4_1, D4_1, A3_1, D3_1, A2_1, D2_1 = get_credential(layout1)
        F_2, A4_2, D4_2, A3_2, D3_2, A2_2, D2_2 = get_credential(layout2)
        F_3, A4_3, D4_3, A3_3, D3_3, A2_3, D2_3 = get_credential(layout3)
        F_4, A4_4, D4_4, A3_4, D3_4, A2_4, D2_4 = get_credential(layout4)

        # 成 5
        if F_1:
            score += SCORE1
        if F_2:
            score += SCORE1
        if F_3:
            score += SCORE1
        if F_4:
            score += SCORE1

        # 活 4
        if A4_1:
            score += SCORE2
        if A4_2:
            score += SCORE2
        if A4_3:
            score += SCORE2
        if A4_4:
            score += SCORE2

        # 双死 4
        if D4_1 and D4_2:
            score += SCORE2
        if D4_1 and D4_3:
            score += SCORE2
        if D4_1 and D4_4:
            score += SCORE2
        if D4_2 and D4_3:
            score += SCORE2
        if D4_2 and D4_4:
            score += SCORE2
        if D4_3 and D4_4:
            score += SCORE2

        # 死 4 活 3
        if D4_1 and A3_2:
            score += SCORE2
        if D4_1 and A3_3:
            score += SCORE2
        if D4_1 and A3_4:
            score += SCORE2

        if D4_2 and A3_1:
            score += SCORE2
        if D4_2 and A3_3:
            score += SCORE2
        if D4_2 and A3_4:
            score += SCORE2

        if D4_3 and A3_1:
            score += SCORE2
        if D4_3 and A3_2:
            score += SCORE2
        if D4_3 and A3_4:
            score += SCORE2

        if D4_4 and A3_1:
            score += SCORE2
        if D4_4 and A3_2:
            score += SCORE2
        if D4_4 and A3_3:
            score += SCORE2

        # 双活 3
        if A3_1 and A3_2:
            score += SCORE3
        if A3_1 and A3_3:
            score += SCORE3
        if A3_1 and A3_4:
            score += SCORE3
        if A3_2 and A3_3:
            score += SCORE3
        if A3_2 and A3_4:
            score += SCORE3
        if A3_3 and A3_4:
            score += SCORE3

        # 死 3 活 3
        if D3_1 and A3_2:
            score += SCORE4
        if D3_1 and A3_3:
            score += SCORE4
        if D3_1 and A3_4:
            score += SCORE4

        if D3_2 and A3_1:
            score += SCORE4
        if D3_2 and A3_3:
            score += SCORE4
        if D3_2 and A3_4:
            score += SCORE4

        if D3_3 and A3_1:
            score += SCORE4
        if D3_3 and A3_2:
            score += SCORE4
        if D3_3 and A3_4:
            score += SCORE4

        if D3_4 and A3_1:
            score += SCORE4
        if D3_4 and A3_2:
            score += SCORE4
        if D3_4 and A3_3:
            score += SCORE4

        # 单死 4
        if [D4_1, D4_2, D4_3, D4_4].count(True) == 1:
            score += SCORE5

        # 单活 3
        if [A3_1, A3_2, A3_3, A3_4].count(True) == 1:
            score += SCORE6

        # 双活 2
        if A2_1 and A2_2:
            score += SCORE7
        if A2_1 and A2_3:
            score += SCORE7
        if A2_1 and A2_4:
            score += SCORE7
        if A2_2 and A2_3:
            score += SCORE7
        if A2_2 and A2_4:
            score += SCORE7
        if A2_3 and A2_4:
            score += SCORE7

        # 单死 3
        if [D3_1, D3_2, D3_3, D3_4].count(True) == 1:
            score += SCORE8

        # 单活 2
        if [A2_1, A2_2, A2_3, A2_4].count(True) == 1:
            score += SCORE9

        # 单死 2
        if [D2_1, D2_2, D2_3, D2_4].count(True) == 1:
            score += SCORE10

    for (x, y) in player_points:
        layout1, layout2, layout3, layout4 = get_layout(False)
        F_1, A4_1, D4_1, A3_1, D3_1, A2_1, D2_1 = get_credential(layout1, False)
        F_2, A4_2, D4_2, A3_2, D3_2, A2_2, D2_2 = get_credential(layout2, False)
        F_3, A4_3, D4_3, A3_3, D3_3, A2_3, D2_3 = get_credential(layout3, False)
        F_4, A4_4, D4_4, A3_4, D3_4, A2_4, D2_4 = get_credential(layout4, False)

        # 成 5
        if F_1:
            score -= SCORE1
        if F_2:
            score -= SCORE1
        if F_3:
            score -= SCORE1
        if F_4:
            score -= SCORE1

        # 活 4
        if A4_1:
            score -= SCORE2
        if A4_2:
            score -= SCORE2
        if A4_3:
            score -= SCORE2
        if A4_4:
            score -= SCORE2

        # 双死 4
        if D4_1 and D4_2:
            score -= SCORE2
        if D4_1 and D4_3:
            score -= SCORE2
        if D4_1 and D4_4:
            score -= SCORE2
        if D4_2 and D4_3:
            score -= SCORE2
        if D4_2 and D4_4:
            score -= SCORE2
        if D4_3 and D4_4:
            score -= SCORE2

        # 死 4 活 3
        if D4_1 and A3_2:
            score -= SCORE2
        if D4_1 and A3_3:
            score -= SCORE2
        if D4_1 and A3_4:
            score -= SCORE2

        if D4_2 and A3_1:
            score -= SCORE2
        if D4_2 and A3_3:
            score -= SCORE2
        if D4_2 and A3_4:
            score -= SCORE2

        if D4_3 and A3_1:
            score -= SCORE2
        if D4_3 and A3_2:
            score -= SCORE2
        if D4_3 and A3_4:
            score -= SCORE2

        if D4_4 and A3_1:
            score -= SCORE2
        if D4_4 and A3_2:
            score -= SCORE2
        if D4_4 and A3_3:
            score -= SCORE2

        # 双活 3
        if A3_1 and A3_2:
            score -= SCORE3
        if A3_1 and A3_3:
            score -= SCORE3
        if A3_1 and A3_4:
            score -= SCORE3
        if A3_2 and A3_3:
            score -= SCORE3
        if A3_2 and A3_4:
            score -= SCORE3
        if A3_3 and A3_4:
            score -= SCORE3

        # 死 3 活 3
        if D3_1 and A3_2:
            score -= SCORE4
        if D3_1 and A3_3:
            score -= SCORE4
        if D3_1 and A3_4:
            score -= SCORE4

        if D3_2 and A3_1:
            score -= SCORE4
        if D3_2 and A3_3:
            score -= SCORE4
        if D3_2 and A3_4:
            score -= SCORE4

        if D3_3 and A3_1:
            score -= SCORE4
        if D3_3 and A3_2:
            score -= SCORE4
        if D3_3 and A3_4:
            score -= SCORE4

        if D3_4 and A3_1:
            score -= SCORE4
        if D3_4 and A3_2:
            score -= SCORE4
        if D3_4 and A3_3:
            score -= SCORE4

        # 单死 4
        if [D4_1, D4_2, D4_3, D4_4].count(True) == 1:
            score -= SCORE5

        # 单活 3
        if [A3_1, A3_2, A3_3, A3_4].count(True) == 1:
            score -= SCORE6

        # 双活 2
        if A2_1 and A2_2:
            score -= SCORE7
        if A2_1 and A2_3:
            score -= SCORE7
        if A2_1 and A2_4:
            score -= SCORE7
        if A2_2 and A2_3:
            score -= SCORE7
        if A2_2 and A2_4:
            score -= SCORE7
        if A2_3 and A2_4:
            score -= SCORE7

        # 单死 3
        if [D3_1, D3_2, D3_3, D3_4].count(True) == 1:
            score -= SCORE8

        # 单活 2
        if [A2_1, A2_2, A2_3, A2_4].count(True) == 1:
            score -= SCORE9

        # 单死 2
        if [D2_1, D2_2, D2_3, D2_4].count(True) == 1:
            score -= SCORE10
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
        this_bitset[x][y] = 1
        computer_points.append((x, y))
        # alpha = max(alpha, Min(alpha, beta, depth + 1))
        val = Min(alpha, beta, depth + 1)
        # 撤销
        this_bitset[x][y] = 0
        computer_points.remove((x, y))

        # 当前层需要求的是极大值
        if val >= alpha:
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
        return evalue()
    for x, y in avaliable_position():
        # 尝试在 (x, y) 处下黑子
        this_bitset[x][y] = 2
        player_points.append((x, y))
        # beta = min(beta, Max(alpha, beta, depth + 1))
        val = Max(alpha, beta, depth + 1)
        # 撤销
        this_bitset[x][y] = 0
        player_points.remove((x, y))

        # 当前层需要求的是极小值
        if val <= beta:
            beta = val
        # alpha 剪枝
        if val <= alpha:
            return alpha
    return beta

class searchThread(threading.Thread):  
    def __init__(self, bitset, count):
        threading.Thread.__init__(self)  
        global this_bitset, this_count
        this_bitset, this_count = bitset, count
          
    def run(self):  
        global computer_played
        computer_played = False
        alpha, beta = -INFINITE, INFINITE
        Max(alpha, beta, 1)
        computer_played = True
