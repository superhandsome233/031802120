# 使用A*算法解题
import heapq
import copy
import re
import datetime
from Ai_puzzle1 import pictureCompare
BLOCK = []  # 给定状态
GOAL = []  # 目标状态

# 4个方向
direction = [[0, 1], [0, -1], [1, 0], [-1, 0]]

# OPEN表
OPEN = []

# 节点的总数
SUM_NODE_NUM = 0

answer = []


# 状态节点
class State(object):
    def __init__(self, gn=0, hn=0, state=None, hash_value=None, par=None):
        '''
        初始化
        :param gn: gn是初始化到现在的距离
        :param hn: 启发距离
        :param state: 节点存储的状态
        :param hash_value: 哈希值，用于判重
        :param par: 父节点指针
        '''
        self.gn = gn
        self.hn = hn
        self.fn = self.gn + self.hn
        self.child = []  # 孩子节点
        self.par = par  # 父节点
        self.state = state  # 局面状态
        self.hash_value = hash_value  # 哈希值

    def __lt__(self, other):  # 用于堆的比较，返回距离最小的
        return self.fn < other.fn

    def __eq__(self, other):  # 相等的判断
        return self.hash_value == other.hash_value

    def __ne__(self, other):  # 不等的判断
        return not self.__eq__(other)


def manhattan_dis(cur_node, end_node):
    '''
    计算曼哈顿距离
    :param cur_state: 当前状态
    :return: 到目的状态的曼哈顿距离
    '''
    cur_state = cur_node.state
    end_state = end_node.state
    dist = 0
    N = len(cur_state)
    for i in range(N):
        for j in range(N):
            if cur_state[i][j] == end_state[i][j]:
                continue
            num = cur_state[i][j]
            if num == 0:
                x = N - 1
                y = N - 1
            else:
                x = num / N  # 理论横坐标
                y = num - N * x - 1  # 理论的纵坐标
            dist += (abs(x - i) + abs(y - j))

    return dist


def generate_child(cur_node, end_node, hash_set, open_table, dis_fn):
    '''
    生成子节点函数
    :param cur_node:  当前节点
    :param end_node:  最终状态节点
    :param hash_set:  哈希表，用于判重
    :param open_table: OPEN表
    :param dis_fn: 距离函数
    :return: None
    '''
    if cur_node == end_node:
        heapq.heappush(open_table, end_node)
        return
    num = len(cur_node.state)
    # print("num is {}".format(num))
    for i in range(0, num):
        for j in range(0, num):
            if cur_node.state[i][j] != 9:
                continue
            for d in direction:  # 四个偏移方向
                x = i + d[0]
                y = j + d[1]
                if x < 0 or x >= num or y < 0 or y >= num:  # 越界了
                    continue
                # 记录扩展节点的个数
                global SUM_NODE_NUM
                SUM_NODE_NUM += 1

                state = copy.deepcopy(cur_node.state)  # 复制父节点的状态
                state[i][j], state[x][y] = state[x][y], state[i][j]  # 交换位置
                # print("state[i][j] is {}".format(state[i][j]))
                # print("state[x][y] is {}".format(state[x][y]))
                h = hash(str(state))  # 哈希时要先转换成字符串
                if h in hash_set:  # 重复了
                    continue
                hash_set.add(h)  # 加入哈希表
                gn = cur_node.gn + 1  # 已经走的距离函数
                hn = dis_fn(cur_node, end_node)  # 启发的距离函数
                node = State(gn, hn, state, h, cur_node)  # 新建节点
                cur_node.child.append(node)  # 加入到孩子队列
                heapq.heappush(open_table, node)  # 加入到堆中


def print_path(node):
    '''
    输出路径
    :param node: 最终的节点
    :return: None
    '''
    num = node.gn

    def show_block(block):
        print("---------------")
        for b in block:
            print(b)
            '''
            try:
                print(b.index(9))
            except ValueError:
                pass
            '''
    stack = []  # 模拟栈
    while node.par is not None:
        stack.append(node.state)
        node = node.par
    stack.append(node.state)
    count=0
    old_line = 0
    old_row = 0
    while len(stack) != 0:
        t = stack.pop()
        show_block(t)
        print(t)
        new_line = 0
        new_row = 0
        flag = 0
        for i in t:
            for j in i:
                if j == 9:
                    flag = 1
                    break
                else:
                    new_row += 1
            if flag == 0:
                new_row = 0
                new_line += 1
            else:
                break
        if count != 0:
            if new_line - old_line == -1:
                answer.append('w')
            if new_line - old_line == 1:
                answer.append('s')
            if new_row - old_row == -1:
                answer.append('a')
            if new_row - old_row == 1:
                answer.append('d')
        old_line = new_line
        old_row = new_row
        count += 1
        # print("9的坐标为[{}][{}]".format(new_line,new_row))

    return num


def A_start(start, end, distance_fn, generate_child_fn, time_limit=10):
    '''
    A*算法
    :param start: 起始状态
    :param end: 终止状态
    :param distance_fn: 距离函数，可以使用自定义的
    :param generate_child_fn: 产生孩子节点的函数
    :param time_limit: 时间限制，默认10秒
    :return: None
    '''
    root = State(0, 0, start, hash(str(BLOCK)), None)  # 根节点
    end_state = State(0, 0, end, hash(str(GOAL)), None)  # 最后的节点
    if root == end_state:
        print("start == end !")

    OPEN.append(root)
    # print("list OPEN is {}".format(OPEN))
    heapq.heapify(OPEN)
    # print("Heapq OPEN is {}".format(OPEN))

    node_hash_set = set()  # 存储节点的哈希值
    node_hash_set.add(root.hash_value)
    start_time = datetime.datetime.now()
    while len(OPEN) != 0:
        top = heapq.heappop(OPEN)
        # print("top is {}".format(top))
        if top == end_state:  # 结束后直接输出路径
            return print_path(top)
        # 产生孩子节点，孩子节点加入OPEN表
        generate_child_fn(cur_node=top, end_node=end_state, hash_set=node_hash_set,
                          open_table=OPEN, dis_fn=distance_fn)
        cur_time = datetime.datetime.now()
        # 超时处理
        if (cur_time - start_time).seconds > time_limit:
            print("Time running out, break !")
            print("Number of nodes:", SUM_NODE_NUM)
            return -1

    print("No road !")  # 没有路径
    return -1


if __name__ == '__main__':

    NUMBER = 3
    win, temp = pictureCompare("./letter1")  # 与分割好的图片进行对比，得到目标矩阵和当前状态矩阵

    GOAL =[ [win[0], win[1], win[2]], [win[3], win[4], win[5]],[ win[6], win[7], win[8]] ]  # 得到目标矩阵

    OPEN = []
    BLOCK = [[temp[0], temp[1], temp[2]], [temp[3], temp[4], temp[5]],[ temp[6], temp[7], temp[8]]] # 原始状态

    SUM_NODE_NUM = 0
    start_t = datetime.datetime.now()
    # 这里添加5秒超时处理，可以根据实际情况选择启发函数
    length = A_start(BLOCK, GOAL, manhattan_dis, generate_child, time_limit=10)
    end_t = datetime.datetime.now()
    if length != -1:
        print("length =", length)
        print("time = ", (end_t - start_t).total_seconds(), "s")
        print("Nodes =", SUM_NODE_NUM)
        print("answer is :",answer)