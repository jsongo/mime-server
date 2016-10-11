#!/usr/bin/env python                                                                                                         
# coding=utf-8
'''
    desc: 生成扫雷地图场景, 在本项目中，雷即指金子
    author: jsongo
'''
import random
# import copy

mimeCnt = 10
col = row = 9

# 生成雷的主入口
def genMimeArr():
    tmpCnt = mimeCnt
    mimeMap = {} # 辅助判断各格子的状态
    
    # 地图场景数据
    data = getInitArr(0)

    # 生成雷
    while tmpCnt > 0:
        randX = getRandPos(col) # x => col
        randY = getRandPos(row) # y => row
        key = '%d-%d' % (randY, randX)
        if not mimeMap.has_key(key):
            mimeMap[key] = 1
            data[randY][randX] = -1 # 用负数来表示这里是雷
            tmpCnt -= 1
    # 扫描雷附近的格子
    for r in xrange(row):
        for c in xrange(col):
            if data[r][c] < 0:
                increaseArround(data, r,c)
    # 打印结果 
    for line in data:
        print(line)
    return data

def getRandPos(max):
    return int(random.random()*10000)%max

def increaseArround(data, r, c):
    # upper row, current row, and the lower row
    for k in xrange(-1, 2): # -1, 0, 1
        rr = r-k # tmp row
        for i in xrange(c-1, c+2):
            cc = i # tmp col
            if (cc >= 0 and cc < col     # 约束列
                and rr >= 0 and rr < row  # 约束行
                and not (rr==r and cc==c)    # 不是当前这一格
                and data[rr][cc] >= 0):  # 且不是雷
                data[rr][cc] += 1

def getInitArr(initValue):
    # 地图场景数据
    data = []
    # 初始化数据
    for r in range(row):
        tmpArr = []
        for c in range(col):
            tmpArr.append(initValue)
        data.append(tmpArr) # 每一行都是一个数组 
    return data

# genMimeArr()
