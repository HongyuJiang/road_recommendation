#!/usr/bin/python
# -*- coding: UTF-8 -*-

from multiprocessing import Pool, freeze_support,Process
import random
import networkx as nx
import math

from road_node import RoadNode  
from driver import Driver  
from customer import Customer 

class GlobalVar:
    def __init__(self):
        self.globalPlanCount = 0
        self.road_links = []
        self.taxisList = []
        self.nodesList = []

# 探索-利用比例 默认为根号2
exploration_ratio = 1.41421

roadIndex2ID = dict()
ID2RoadIndex = dict()
ID2RoadIndex[-1] = -1

def getRandom():
  return random.random()

# 获得一个随机的道路ID
def getARandomNode(nodesList):
  return nodesList[random.randint(0, len(nodesList)-1)]

# 构建道路网络
def buidingNetwork(links,nodesList):

  network = dict()

  for link in links:
    source = roadIndex2ID[link[0]]
    target = roadIndex2ID[link[1]]

    if source in network:
      network[source][target] = nodesList[roadIndex2ID[link[0]]].getLength()
    else:
      network[source] = dict()
      network[source][target] = nodesList[roadIndex2ID[link[0]]].getLength()

    if target in network:
      network[target][source] = nodesList[roadIndex2ID[link[1]]].getLength()
    else:
      network[target] = dict()
      network[target][source] = nodesList[roadIndex2ID[link[1]]].getLength()
      
  return network

# 获得两个节点之间的最短路径长度，采用迪杰特斯拉算法
def get_shortest_path_length(source, target, G, vars):

  paths = []

  try:
    
    shortest_path = list(nx.shortest_path(G, source = source, target = target))
    #print(shortest_path)
    for node_index in range(len(shortest_path)):
      node = shortest_path[node_index]
      paths.append({'node':node,'length':vars.nodesList[node].getLength()})
  except:
    return []
  else:
    return paths
  
  return paths

# 帮助出租车选择下一段路
def next_road_selection(location,network,vars):

  truly_candidates = []

  #print(network.keys())

  for candidate_index in network[location]:
    
    vars.nodesList[candidate_index].candidateIncrement()

    #print(location, candidate_index, network[location][candidate_index])
    
    if network[location][candidate_index] >= 0:
      
      UCB = vars.nodesList[candidate_index].setUCBValue(vars.globalPlanCount, exploration_ratio)

      UCBValue = vars.nodesList[candidate_index].getUCBValue()
      busy_time = vars.nodesList[candidate_index].getLength()
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

def game_round(round_index,vars,network, G):

  for node_index in range(len(vars.nodesList)):
      vars.nodesList[node_index].produceCustomer()

  for taxis_index in range(len(vars.taxisList)):
    
    # state means whether have customer
    # 0: Empty
    # 1: Full
    isOccupation = vars.taxisList[taxis_index].getOccupation()
    location = vars.taxisList[taxis_index].getLocation()
    region = vars.nodesList[location].getRegion()
    runingCondition = vars.taxisList[taxis_index].runingARound()
    # 当前出租车没有载客
    if not isOccupation:
      #print(vars.nodesList[location].getCustomerCount())
      # 如果出租车所在的位置发现乘客
      if vars.nodesList[location].getCustomerCount() > 0:
        #print('载客')
        #destination_candidates = vars.regionDict[region]
        #destination_ID = destination_candidates[random.randint(0, len(destination_candidates)-1)]
        destination_ID = getARandomNode(vars.nodesList).getID()
        # 载客
 
        paths = get_shortest_path_length(location,destination_ID,G,vars)
        total_length = 0
        for index in range(len(paths)):
          total_length += paths[index]['length']

        #print(location,destination_ID,total_length)

        if len(paths) > 0 and total_length > 40:
          #print('pick')
          vars.taxisList[taxis_index].pickACustomer(destination_ID, paths)
          vars.nodesList[location].customerReduce()
          vars.nodesList[location].hittedIncrement()
        #print(vars.nodesList[location].getCustomerCount())
        
        continue 
      
      # 如果出租车所在的位置没有发现乘客
      else:
          # runingCondition 中 1 代表下客， 2 表示将进入下一个道路， 0 表示没有状态更新
          if runingCondition == 2:
              # 进入下一段道路
              vars.globalPlanCount += 1
              #print('source:' + str(location))
              #print(location in network)
              nextLocation = next_road_selection(location,network,vars)
              #print('target:' + str(nextLocation))
              planCost = vars.nodesList[nextLocation].getLength()
              vars.taxisList[taxis_index].changeSegment(nextLocation, planCost)

def process(vars,network,G):

   nodes_num = len(vars.nodesList)

   for round_index in range(3000):
    print('############## round: ' + str(round_index) + ' Global Plan Count: ' + str(vars.globalPlanCount))
    game_round(round_index,vars,network,G)
    nodeCustomerStatus = []
    nodeUCBStatus = [] 
    taxisStatus = []


    for index in range(20):
      nodeCustomerStatus.append(vars.nodesList[index].getCustomerCount())

    for index in range(len(vars.nodesList)):
      nodeUCBStatus.append(vars.nodesList[index].getUCBValue())

    for index in range(20):
      taxisStatus.append(vars.taxisList[index].getOccupation())

    output = open('realtime.data.4.csv','a+')
    if round_index < 1000:
      for index in range(len(vars.taxisList)):
        output.write(str(round_index) + ',' + str(index) + ',' + str(ID2RoadIndex[vars.taxisList[index].getLocation()]) + ',' + str(ID2RoadIndex[vars.taxisList[index].getPlanLocation()]) + ',' + str(vars.taxisList[index].getBusyTime()) + ',' + str(vars.taxisList[index].getCDTime()) + ',' + str(vars.taxisList[index].getOccupation()) + '\n')

    print('############## customer status: ' + str(nodeCustomerStatus))
    print('############## taxis status: ' + str(taxisStatus))
    print('############## UCB values: ' + str(nodeUCBStatus[0:10]))

  
def main():

  globalPlanCount = 0
  nodes_num = 0
  taxis_num = 3000
  road_links = []
  taxisList = []
  nodesList = []
  links_list = []
  source_dict = dict()
  regionDict = dict()

  # 生成道路节点
  links_file = open('links.csv')
  counter = 0 
  for line in links_file:

    counter += 1
    if counter > 1:
      meta = line.split(',')

      startX = float(meta[9])
      endX = float(meta[11])
      startY = float(meta[10])
      endY = float(meta[12])
      
      #print(startX, startY)
      if not (startY < 40.876760 and startY > 40.702641 and startX < -73.905251 and startX > -74.022418):
        if not (endY < 40.876760 and endY > 40.702641 and startY < -73.905251 and startY > -74.022418):
          continue
      
      _name = int(meta[0])
      _length = int(float(meta[5])/50)
      #print(_length)
      _source = meta[1]
      _target = meta[2]
      _region = meta[5]

      ele = dict()
      ele['source'] = _source
      ele['target'] = _target
      ele['id'] = _name
      links_list.append(ele)

      if _source in source_dict:
        source_dict[_source][_target] = _name
      else:
        source_dict[_source] = dict()
        source_dict[_source][_target] = _name

      roadIndex2ID[_name] = len(nodesList)
      ID2RoadIndex[len(nodesList)] = _name

      node = RoadNode(_name, _length, _region)
      nodesList.append(node)

      if _region not in regionDict:
        regionDict[_region] = []
        regionDict[_region].append(roadIndex2ID[_name])
      else:
        regionDict[_region].append(roadIndex2ID[_name])

  road_links = []
  nodes_num = len(links_list)

  for link_index in range(len(links_list)):
    link = links_list[link_index]
    source = link['target']
    if source in source_dict:
      targets = list(source_dict[source].keys())
      for target_index in range(len(targets)):
        target = targets[target_index]
        #print(link['id'], source_dict[source][target])
        road_links.append([link['id'], source_dict[source][target]])
        # 检测是否存在道路闭环
        if link['id'] == source_dict[source][target]:
          print('闭环')

  #print(len(nodesList))
  # 生成出租车
  for i in range(taxis_num):
      #_origin = getARandomNode(nodesList).getID()
      _origin = random.randint(0, len(nodesList)-1)
      _length = nodesList[_origin].getLength()
      taxi = Driver(_origin, _length)
      taxisList.append(taxi)

  print('Network building')
  network = buidingNetwork(road_links, nodesList)

  G = nx.Graph()
  for link_index in range(len(road_links)):
    link = road_links[link_index]
    
    s = roadIndex2ID[link[0]]
    t = roadIndex2ID[link[1]]
    w = network[s][t]
    G.add_edge(s, t, weight = w)

  global_vars = GlobalVar()

  global_vars.globalPlanCount = globalPlanCount
  global_vars.taxisList = taxisList
  global_vars.nodesList = nodesList
  global_vars.regionDict = regionDict
  process(global_vars,network,G)
  
  output = open('result.csv', 'w')

  for index in range(len(global_vars.nodesList)):

    output.write(str(global_vars.nodesList[index].getID()) + ',' + str(global_vars.nodesList[index].getProductionRate()) + ',' + str(global_vars.nodesList[index].getUCBValue()) + '\n')

  print('---------------finished----------------')
  

if __name__ == "__main__":
  freeze_support()
  main()