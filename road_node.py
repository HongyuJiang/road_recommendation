#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random
import math

# 路网中路段类
class RoadNode:
    empCount = 0
    def __init__(self, ID, length,region):
        # 被选为候选节点的次数
        self.selectedAsCandidateCount = 0
        # 成功在该道路载客的次数
        self.hittedCount = 0
        # 道路需要乘车的乘客数量
        self.customerCount = 0
        # 道路UCB值
        self.UCBValue = 0
        # 道路产生乘客的概率
        self.productionRate = random.random() / 100
        # 道路ID, 方便进行索引
        self.ID = ID
        # 道路长度
        self.length = length
        # 道路所在大道
        self.region = region

    # 设置节点的UCB值
    def setUCBValue(self, globalPlanCount, exploration_ratio):
        if self.selectedAsCandidateCount == 0 or globalPlanCount == 0:
            return 0
        else:
            self.UCBValue = self.hittedCount + exploration_ratio * math.sqrt(math.log(globalPlanCount) / self.selectedAsCandidateCount)
            return self.UCBValue
            
    # 获取节点的UCB值
    def getUCBValue(self):
        return self.UCBValue

    # 增加一次被选作候选者的次数
    def candidateIncrement(self):
         self.selectedAsCandidateCount += 1
    
    # 增加一次被选中的次数
    def hittedIncrement(self):
         self.hittedCount += 1

    # 产生一个新的乘客
    def produceCustomer(self):
        if random.random() <= self.productionRate:
            self.customerCount += 1

    # 减少一个乘客
    def customerReduce(self):
        self.customerCount -= 1

    # 获取道路长度
    def getLength(self):
        return self.length

    # 获取道路乘客数量
    def getCustomerCount(self):
        return self.customerCount

    # 获取道路ID
    def getID(self):
        return self.ID

    # 获取所在大道
    def getRegion(self):
        return self.region

    def getProductionRate(self):
        return self.productionRate


    