#!/usr/bin/python
# -*- coding: UTF-8 -*-

import random

import networkx as nx

import math

from road_node import RoadNode  
from driver import Driver  
from customer import Customer 

G = nx.Graph()

# 探索-利用比例 默认为根号2
exploration_ratio = 1.41421

# 全局道路规划次数
globalPlanCount = 0

# 道路数量
nodes_num = 10

# 出租车数量
taxis_num = 10

# 道路列表
nodesList = []

# 出租车列表
taxisList = []

# 道路连接情况
road_links = [[0,1], [0,2], [1,3], [1,4], [2,5], [2,6], [3,7], [3,8], [4,9]]

def getRandom():
  return random.random()

# 获得一个随机的道路ID
def getARandomNode():
  return nodesList[random.randint(0, nodes_num-1)].getID()

# 构建道路网络
def buidingNetwork(links):
  network = []
  for row_index in range(nodes_num):
    row = []
    for colum_index in range(nodes_num):
      row.append(-1)
    network.append(row) 
  for link in links:
    
    source = link[0]
    target = link[1]
    
    distance_source = nodesList[link[0]].getLength()
    distance_target = nodesList[link[1]].getLength()
    
    network[source][target] = distance_source
    network[target][source] = distance_target
  
  return network

# 获得两个节点之间的最短路径长度，采用迪杰特斯拉算法
def get_shortest_path_length(network, source, target):
  
  for link_index in range(len(road_links)):
    link = road_links[link_index]
    
    s = link[0]
    t = link[1]
    w = network[s][t]
    G.add_edge(s, t, weight = w)
  
  path_length = 0
  shortest_path = nx.dijkstra_path(G, source, target)
  for node_index in range(len(shortest_path)):
    node = shortest_path[node_index]
    path_length += nodesList[node].getLength()
  
  return path_length

# 帮助出租车选择下一段路
def next_road_selection(network, location):
  
  truly_candidates = []
  next_step_candicates = network[location]
  for candidate_index in range(len(next_step_candicates)):
    
    nodesList[candidate_index].candidateIncrement()
    
    if network[location][candidate_index] != 0:
      
      nodesList[candidate_index].setUCBValue(globalPlanCount, exploration_ratio)

      UCBValue = nodesList[candidate_index].getUCBValue()
      busy_time = nodesList[candidate_index].getLength()
      info_meta = [UCBValue, busy_time, candidate_index]
      truly_candidates.append(info_meta)
  
  max_UCB = 0
  max_UCB_index = 0
  
  for index in range(len(truly_candidates)):
    UCB = truly_candidates[index][0]
    if UCB > max_UCB:
      max_UCB = UCB
      max_UCB_index = index

  max_UCB_next_location = truly_candidates[max_UCB_index][2]
  
  return max_UCB_next_location

def game_round(network, round_index):
  
  global globalPlanCount
  
  for node_index in range(nodes_num):
      nodesList[node_index].produceCustomer()

  for taxis_index in range(taxis_num):
    
    # state means whether have customer
    # 0: Empty
    # 1: Full
    isOccupation = taxisList[taxis_index].getOccupation()
    location = taxisList[taxis_index].getLocation()
    runingCondition = taxisList[taxis_index].runingARound()
    # 当前出租车没有载客
    if not isOccupation:

      # 如果出租车所在的位置发现乘客
      if nodesList[location].getCustomerCount() > 0:
        destination = nodesList[getARandomNode()]
        destination_ID = nodesList[getARandomNode()].getID()

        # 载客
        taxisList[taxis_index].pickACustomer(destination_ID, get_shortest_path_length(network, location, destination_ID))
        
        globalPlanCount += 1
        nodesList[location].customerReduce()
        nodesList[location].hittedIncrement()
        
        continue 
      
      # 如果出租车所在的位置没有发现乘客
      else:
          # runingCondition 中 1 代表下客， 2 表示将进入下一个道路， 0 表示没有状态更新
          if runingCondition == 2:
              # 进入下一段道路
              nextLocation = next_road_selection(network, location)
              planCost = nodesList[nextLocation].getLength()
              taxisList[taxis_index].changeSegment(nextLocation, planCost)
  
  
def main():

  # 生成道路节点
  for i in range(nodes_num):
      _productionRate = getRandom()/10
      _length = int(getRandom() * 10) + 5
      node = RoadNode(i, _productionRate, _length)
      nodesList.append(node)

  # 生成出租车
  for i in range(taxis_num):
      _origin = getARandomNode()
      _length = nodesList[_origin].getLength()
      taxi = Driver(_origin, _length)
      taxisList.append(taxi)
  
  
  network = buidingNetwork(road_links)
  for round_index in range(1000):
    game_round(network, round_index)
    nodeCustomerStatus = []
    nodeUCBStatus = [] 
    for index in range(nodes_num):
      nodeCustomerStatus.append(nodesList[index].getCustomerCount())
      nodeUCBStatus.append(int(nodesList[index].getUCBValue()))
    print('############## round: ' + str(round_index))
    print('############## customer: ' + str(nodeCustomerStatus))
    print('############## UCB: ' + str(nodeUCBStatus))

if __name__ == "__main__":
  main()