#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 司机类
class Driver:
    empCount = 0
    def __init__(self, origin, timeSpend):
        # 载客次数
        self.pickUpCount = 0
        # 出租车位置
        self.location = origin
        # 是否有客
        self.occupation = False
        # 希望到达的位置
        self.planLocation = -1
        # 到达终点还剩时间
        self.busyTime = 0
        # 选择下一个路段的冷却时间
        self.CDTime = timeSpend

    # 载客
    def pickACustomer(self, destination, timeSpend):
        print(destination, timeSpend)
        self.pickUpCount += 1
        self.occupation = True
        self.planLocation = destination
        self.busyTime = timeSpend
 
    # 下客
    def dropACustomer(self):
        self.occupation = False
        self.location = self.planLocation
        self.planLocation = -1

    # 进入下一个路段
    def changeSegment(self, nextSegment, nextTimeSpend):
        self.location = nextSegment
        self.CDTime = nextTimeSpend

    # 运行一个回合
    def runingARound(self):
        condition = 0
        # 进入下一路段时间
        if self.CDTime > 0:
            self.CDTime -= 1
        # 准备进入下一路段
        if self.CDTime == 0:
            condition = 2
        # 如果有乘客
        if self.occupation:
            # 如果乘客还未到终点
            if self.busyTime > 0:
                self.busyTime -= 1
            # 如果乘客到达终点
            if self.busyTime == 0:
                self.dropACustomer()
                condition = 1
        return condition

    # 获取CD时间
    def getCDTime(self):
        return self.CDTime

    # 获取载客状态
    def getOccupation(self):
        return self.occupation

    # 获取当前位置
    def getLocation(self):
        return self.location

    # 获取目的位置
    def getPlanLocation(self):
        return self.planLocation
