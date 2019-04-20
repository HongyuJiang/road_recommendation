#!/usr/bin/python
# -*- coding: UTF-8 -*-

# 当前类并没有被使用
# 乘客类
class Customer:
    def __init__(self, origin, destination):
        # 乘客起始位置
        self.origin = origin
        # 乘客目标位置
        self.destination = destination
    
    # 获取乘客起始位置
    def getOrigin(self):
        return self.origin
    
    # 获取乘客目标位置
    def getDestination(self):
        return self.destination