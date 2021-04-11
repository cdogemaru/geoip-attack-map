from collections import defaultdict
import copy, os, math, pickle, random, time, xgboost, json, re
import networkx as nx
import numpy as np
from xgboost import XGBClassifier
from multiprocessing import Process, Queue
import multiprocessing

class Model_Sample(object):
    def __init__(self):
        self.in_frequency = defaultdict(int)
        self.out_frequency = defaultdict(int)
        self.linkfreq = defaultdict(int)
        self.linkorder = defaultdict(list)
        self.allasns = set()
        self.AS2country = json.loads(open('./AS2country.json').read())

        with open('./joinfreq1_201901.txt') as f:
            for line in f:
                [flag, key, num] = line.strip().split(' ')
                if flag == 'in':
                    self.in_frequency[key] = int(num)
                elif flag == 'out':
                    self.out_frequency[key] = int(num)
        
        with open('./linkfreq1_201901.txt') as f:
            for line in f:
                [link, num] = line.strip().split(' ')
                self.linkfreq[tuple(link.split('|'))] = int(num)

        with open('./linkorder1_201901.txt') as f:
            for line in f:
                [node, neighbor] = line.strip().split(' ')
                self.linkorder[node] = neighbor.split('|')

        with open('./allasns_bigdata1_201901.txt') as f:
            for line in f:
                self.allasns = set(line.strip().split(' '))
                
        self.relationship = dict()
        self.provider, self.peer, self.customer = defaultdict(set), defaultdict(set), defaultdict(set)
        ##############################################################
        self.extend_relationship = dict()
        self.extend_provider, self.extend_peer, self.extend_customer = defaultdict(set), defaultdict(set), defaultdict(set)
        ##############################################################
        with open('./asrel_rib1_201901.txt') as f:
            for line in f:
                [asn1, asn2, r] = line.strip().split('|')
                if r == '-1':
                    self.relationship[(asn1, asn2)] = 'p2c'
                    self.relationship[(asn2, asn1)] = 'c2p'
                    self.customer[asn1].add(asn2)
                    self.provider[asn2].add(asn1)
                else:
                    self.relationship[(asn1, asn2)] = 'p2p'
                    self.relationship[(asn2, asn1)] = 'p2p'
                    self.peer[asn1].add(asn2)
                    self.peer[asn2].add(asn1)
        
        self.core_cluster = set()
        with open('./core_shell_201901.txt') as f:
            for line in f:
                info = line.strip().split(' ')
                if int(info[1]) > 1000:
                    self.core_cluster.add(info[0])

    def get_sample(self, path):
        att = [len(path), self.shortest[(path[0], path[-1])] if (path[0], path[-1]) in self.shortest else len(path)]
        att.extend([round(math.log(len(self.extend_provider[path[-1]])+1)), round(math.log(len(self.extend_peer[path[-1]])+1)), round(math.log(len(self.extend_customer[path[-1]])+1))])
        att.extend([round(math.log(len(self.extend_provider[path[-2]])+1)), round(math.log(len(self.extend_peer[path[-2]])+1)), round(math.log(len(self.extend_customer[path[-2]])+1))])

        if path[-1] in self.core_cluster:
            for i in range(len(path), 0, -1):
                if i == 1:
                    att.extend([1, 0])
                else:
                    temp = '|'.join(path[-i:])
                    if temp in self.in_frequency:
                        att.extend([i, int(math.log(self.in_frequency[temp]))+1])
                        break 
            att.append(round(math.log(self.linkfreq[(path[-1], path[-2])] + 1)))
        
        if path[-2] not in self.linkorder[path[-1]]:
            att.append(-1)
        else:
            att.append(self.linkorder[path[-1]].index(path[-2]))
        if path[-1] not in self.linkorder[path[-2]]:
            att.append(-1)
        else:
            att.append(self.linkorder[path[-2]].index(path[-1]))
        
    
        for i in range(len(path), 0, -1):
            if i == 1:
                att.extend([1, 0])
            else:
                temp = '|'.join(path[-i:][::-1])
                if temp in self.out_frequency:
                    att.extend([i, int(math.log(self.out_frequency[temp]))+1])
                    break #2
        
        for i in range(len(path), 0, -1):
            if i == 1:
                att.extend([1, 0])
            else:
                temp = '|'.join(path[:i])
                if temp in self.out_frequency:
                    att.extend([i, int(math.log(self.out_frequency[temp]))+1])
                    break
        
        rel = []
        for i in range(len(path) - 1):
            rel.append(self.extend_relationship[(path[i], path[i + 1])])
        att.extend([rel.count('c2p'), rel.count('p2p'), rel.count('p2c')]) #3
        
        if path[-1] not in self.AS2country or path[-2] not in self.AS2country or not set(self.AS2country[path[-1]]) & set(self.AS2country[path[-2]]):
            att.append(0)
        else:
            att.append(1)

        slen, slen1 = (self.shortest[(path[0], path[-1])] if (path[0], path[-1]) in self.shortest else len(path)), (self.shortest[(path[0], path[-2])] if (path[0], path[-2]) in self.shortest else (len(path) - 1))
        att.extend([len(path) - slen, len(path) - 1 - slen1])

        if path[0] in self.allasns:
            att.append(0)
        else:
            att.append(1)
        
        return att

    def simulate(self, asn):
        self.AS_path = defaultdict(list)
        self.worst = defaultdict(list)
        self.path_flag = dict()
        self.AS_path[asn] = [asn]
        self.worst[asn] = [asn]
        self.path_flag[tuple([asn])] = 0
        self.stream(asn)

        self.shortest = dict()
        for key in self.AS_path:
            self.shortest[(asn, key)] = len(self.AS_path[key])
    
    def condition(self, current, neighbor):
        valleyfree = False
        if self.path_flag[current] == 0:
            valleyfree = True
        elif self.path_flag[current] != 0 and neighbor in self.customer[current[-1]]:
            valleyfree = True
        return valleyfree

    def smaller(self, link1, link2):
        (asn1, asn2) = link1
        (asn3, asn4) = link2
        if asn1 in self.extend_customer[asn2] and (asn3 in self.extend_peer[asn4] or asn3 in self.extend_provider[asn4]):
            return True
        elif asn1 in self.extend_peer[asn2] and asn3 in self.extend_provider[asn4]:
            return True
        return False

    def stream(self, asn):
        active, candicate = [tuple([asn])], []
        relationship_list = [self.extend_provider, self.extend_peer, self.extend_customer]
        
        while len(active) > 0:
            for i in range(3):
                relationship = relationship_list[i]
                for current in active:
                    for neighbor in relationship[current[-1]]:
                        if neighbor == asn:
                            continue
                        if self.condition(current, neighbor):
                            right_path = list(current) + [neighbor]
                            if len(self.AS_path[neighbor]) == 0 or len(right_path) < len(self.AS_path[neighbor]):
                                self.AS_path[neighbor] = copy.deepcopy(right_path)
                                self.path_flag[tuple(right_path)] = i
                                candicate.append(tuple(right_path))
                                if len(self.worst[neighbor]) == 0 or self.smaller((current[-1], neighbor), (self.worst[neighbor][-2], self.worst[neighbor][-1])):
                                    self.worst[neighbor] = copy.deepcopy(right_path)
                            elif self.smaller((current[-1], neighbor), (self.worst[neighbor][-2], self.worst[neighbor][-1])):
                                self.worst[neighbor] = copy.deepcopy(right_path)
                                self.path_flag[tuple(right_path)] = i
                                candicate.append(tuple(right_path))
            
            active = copy.deepcopy(candicate)
            active.sort(key = lambda x: int(x[-1]))
            candicate = []

class Routingtree(object):
    def __init__(self):
        self.ms = Model_Sample()
        self.threshold = 0.5
        
    def condition(self, current, neighbor):
        if neighbor in current or len(current) >= 9:
            return False
        slen = self.ms.shortest[(current[0], neighbor)] if (current[0], neighbor) in self.ms.shortest else len(current) + 1
        if len(current) + 1 - slen > 2:
            return False
        
        valleyfree = False
        if self.path_flag[current] == 0:
            valleyfree = True
        elif self.path_flag[current] != 0 and neighbor in self.ms.customer[current[-1]]:
            valleyfree = True
        return valleyfree

    def get_model(self, paths, model_name):
        atts = list()
        for path in paths:
            atts.append(self.ms.get_sample(path))
        atts = np.array(atts)
        predict = self.model[model_name].predict_proba(atts)
        return (list([value[1] for value in predict]))

    def add_path(self, paths):
        candicate = set()
        for model_name in paths:
            result = self.get_model(paths[model_name], model_name)
            for i in range(len(result)):
                neighbor = paths[model_name][i][-1]
                self.spread_score[paths[model_name][i]] = result[i]

                if len(self.AS_path[neighbor]) == 0:
                    self.AS_path[neighbor].append(paths[model_name][i])
                    candicate.add(paths[model_name][i])
                else:
                    if self.spread_score[self.AS_path[neighbor][0]] <= self.threshold and self.spread_score[self.AS_path[neighbor][0]] < result[i]:
                        self.AS_path[neighbor][0] = paths[model_name][i]
                        candicate.add(paths[model_name][i])
                    elif self.spread_score[self.AS_path[neighbor][0]] > self.threshold and result[i] > self.threshold:
                        self.AS_path[neighbor].append(paths[model_name][i])
                        candicate.add(paths[model_name][i])
        return candicate

    def get_model_name(self, right_path):
        if right_path[-1] in self.ms.core_cluster:
            cate = 'core'
        else:
            cate = 'shell'
        slen = self.ms.shortest[(right_path[0], right_path[-1])] if (right_path[0], right_path[-1]) in self.ms.shortest else len(right_path)
        if slen <= 3:
            return cate + '1'
        elif slen <= 5:
            return cate + '2'
        else:
            return cate + '3'

    def stream(self, asn):
        active, candicate = [tuple([asn])], set()
        relationship_list = [self.ms.extend_provider, self.ms.extend_peer, self.ms.extend_customer]
        
        for epoch in range(9):
            paths = defaultdict(list)
            for i in range(3):
                relationship = relationship_list[i]
                for current in active:
                    for neighbor in relationship[current[-1]]:
                        if self.condition(current, neighbor):
                            right_path = tuple(list(current) + [neighbor])
                            self.path_flag[right_path] = i
                            paths[self.get_model_name(right_path)].append(right_path)
            candicate = self.add_path(paths)
            for path in self.sample_dict:
                if len(path) == epoch + 2:
                    self.spread_score[path] = 1.01
                    if path not in self.AS_path[path[-1]]:
                        self.AS_path[path[-1]].append(path)
                    if path in self.path_flag:
                        candicate.add(path)
            active = list(candicate)
            active.sort(key = lambda x: int(x[-1]))
            candicate = set()
    
    def argus_simulate(self, json_info, name, category):
        origin = json_info[name]
        self.ms.extend_relationship = copy.deepcopy(self.ms.relationship)
        self.ms.extend_provider, self.ms.extend_peer, self.ms.extend_customer = copy.deepcopy(self.ms.provider), copy.deepcopy(self.ms.peer), copy.deepcopy(self.ms.customer)
        self.AS_path = defaultdict(list)
        self.AS_path[origin] = [tuple([origin])]
        self.spread_score = defaultdict(float)
        self.spread_score[tuple([origin])] = 1.01
        self.path_flag = dict()
        self.path_flag[tuple([origin])] = 0

        self.sample_dict = set()
        if category == 'attacker':
            for info in json_info['vps']:
                path = tuple(info['path'].split(' ')[::-1])
                if path[0] != origin:
                    continue
                for i in range(len(path)):
                    self.sample_dict.add(path[:i + 1])
                vf_flag = 0
                for i in range(1, len(path)):
                    if vf_flag == 0:
                        if (path[i - 1], path[i]) not in self.ms.extend_relationship:
                            self.ms.extend_relationship[(path[i - 1], path[i])] = 'c2p'
                            self.ms.extend_relationship[(path[i], path[i - 1])] = 'p2c'
                            self.ms.extend_provider[path[i - 1]].add(path[i])
                            self.ms.extend_customer[path[i]].add(path[i - 1])
                        elif path[i] in self.ms.peer[path[i - 1]]:
                            vf_flag = 1
                        elif path[i] in self.ms.customer[path[i - 1]]:
                            vf_flag = 2
                    else:
                        if (path[i] in self.ms.provider[path[i - 1]]) or (path[i] in self.ms.peer[path[i - 1]]):
                            break
                        elif (path[i] in self.ms.customer[path[i - 1]]) or ((path[i - 1], path[i]) not in self.ms.extend_relationship):
                            vf_flag = 2
                            self.ms.extend_relationship[(path[i - 1], path[i])] = 'p2c'
                            self.ms.extend_relationship[(path[i], path[i - 1])] = 'c2p'
                            self.ms.extend_customer[path[i - 1]].add(path[i])
                            self.ms.extend_provider[path[i]].add(path[i - 1])
                    self.path_flag[path[:i + 1]] = vf_flag

        self.ms.simulate(origin)
        self.stream(origin)

    def first_epoch(self, json_info):
        self.model = dict()
        for cate in ['core', 'shell']:
            for num in ['1', '2', '3']:
                model_name = cate + num
                self.model[model_name] = pickle.load(
                    open('./xgboost_201901_1_' + model_name + '.model', 'rb'))
        
        output_json = list()
        self.argus_simulate(json_info, 'oldhomeas', 'victim')

        for key in self.AS_path:
            max_score, max_str = 0.0, None
            for path in self.AS_path[key]:
                if self.spread_score[path] > max_score:
                    max_str = path
                    max_score = self.spread_score[path]
            output_json.append({'asn': key, 'path': ' '.join(max_str[::-1])})
                
        return output_json

    def second_epoch(self, json_info):
        self.model = dict()
        for cate in ['core', 'shell']:
            for num in ['1', '2', '3']:
                model_name = cate + num
                self.model[model_name] = pickle.load(
                    open('./xgboost_201901_1_' + model_name + '.model', 'rb'))
        
        output_json = list()
        if json_info['type'] == 0: #origin
            result_path, result_score = dict(), dict()
            for name in ['oldhomeas', 'newhomeas']:
                self.argus_simulate(json_info, name, 'attacker')
                result_path[name] = copy.deepcopy(self.AS_path)
                result_score[name] = copy.deepcopy(self.spread_score)

            for key in set(result_path['oldhomeas'].keys()) | set(result_path['newhomeas'].keys()):
                max_score, max_str = 0.0, None
                for name in ['oldhomeas', 'newhomeas']:
                    for path in result_path[name][key]:
                        if result_score[name][path] > max_score:
                            max_str = path
                            max_score = result_score[name][path]
                output_json.append({'asn': key, 'path': ' '.join(max_str[::-1]), 'is_affected': 1 if max_str[0] == json_info['newhomeas'] else 0})
                
        else:
            result_path, result_score = dict(), dict()
            self.argus_simulate(json_info, 'oldhomeas', 'attacker')
            result_path = copy.deepcopy(self.AS_path)
            result_score = copy.deepcopy(self.spread_score)

            for key in self.AS_path:
                max_score, max_str = 0.0, None
                for path in self.AS_path[key]:
                    if result_score[path] > max_score:
                        max_str = path
                        max_score = result_score[path]
                output_json.append({'asn': key, 'path': ' '.join(max_str[::-1]), 'is_affected': 1 if json_info['bad_path_segment'] in ' '.join(max_str[::-1]) else 0})
                
        return output_json


if __name__ == '__main__':
    rt = Routingtree()
    #rt.second_epoch({'vps': [{'is_affected': 1, 'path': '207044 3257 2914 45474 263009 52993', 'asn': '207044'}], 
    #    'oldhomeas': '61670', 'bad_path_segment': '', 'alarm_id': 10015888, 'newhomeas': '52993', 'type': 0})
    rt.first_epoch({'oldhomeas': '0', 'bad_path_segment': u'50313 39153', 'alarm_id': 10028627, 'newhomeas': '0', 'type': 1})
    rt.second_epoch({'vps': [{'is_affected': 1, 'path': u'54574 6461 1299 50313 39153 56690', 'asn': u'54574'}, 
        {'is_affected': 1, 'path': u'2497 1299 50313 39153 56690', 'asn': u'2497'}, 
        {'is_affected': 1, 'path': u'20514 1299 50313 39153 56690', 'asn': u'20514'}, 
        {'is_affected': 0, 'path': u'132825 3491 1299 50313 12314 56690', 'asn': u'132825'}, 
        {'is_affected': 0, 'path': u'53070 2914 1299 50313 12314 56690', 'asn': u'53070'}, 
        {'is_affected': 0, 'path': u'35266 2914 1299 50313 12314 56690', 'asn': u'35266'}], 
        'oldhomeas': '0', 'bad_path_segment': u'50313 39153', 'alarm_id': 10028627, 'newhomeas': '0', 'type': 1})
    exit()
    rt.second_epoch({'vps': [{'is_affected': 1, 'path': u'29691 1299 3257 29119 31577 211808', 'asn': u'29691'}, 
        {'is_affected': 1, 'path': u'58057 34549 1299 3257 29119 31577 211808', 'asn': u'58057'}, 
        {'is_affected': 1, 'path': u'34854 1299 3257 29119 31577 211808', 'asn': u'34854'}, 
        {'is_affected': 1, 'path': u'39351 29119 31577 211808', 'asn': u'39351'}, 
        {'is_affected': 1, 'path': u'57695 3214 1299 3257 29119 31577 211808', 'asn': u'57695'}, 
        {'is_affected': 1, 'path': u'20514 1299 3257 29119 31577 211808', 'asn': u'20514'}, 
        {'is_affected': 1, 'path': u'34549 1299 3257 29119 31577 211808', 'asn': u'34549'}, 
        {'is_affected': 1, 'path': u'139589 49752 137490 43350 29119 31577 211808', 'asn': u'139589'}, 
        {'is_affected': 1, 'path': u'51999 39533 13030 1299 3257 29119 31577 211808', 'asn': u'51999'}, 
        {'is_affected': 1, 'path': u'51873 9002 3356 3257 29119 31577 211808', 'asn': u'51873'}, 
        {'is_affected': 1, 'path': u'48362 3356 3257 29119 31577 211808', 'asn': u'48362'}, 
        {'is_affected': 1, 'path': u'34553 44684 1299 3257 29119 31577 211808', 'asn': u'34553'}, 
        {'is_affected': 1, 'path': u'328474 328112 37271 3257 29119 31577 211808', 'asn': u'328474'}, 
        {'is_affected': 1, 'path': u'47147 1299 3257 29119 31577 211808', 'asn': u'47147'}, 
        {'is_affected': 1, 'path': u'60945 1299 3257 29119 31577 211808', 'asn': u'60945'}, 
        {'is_affected': 1, 'path': u'29467 2914 3257 29119 31577 211808', 'asn': u'29467'}, 
        {'is_affected': 1, 'path': u'12779 2914 3257 29119 31577 211808', 'asn': u'12779'}, 
        {'is_affected': 1, 'path': u'49697 61438 39912 1299 3257 29119 31577 211808', 'asn': u'49697'}, 
        {'is_affected': 1, 'path': u'199524 174 3257 29119 31577 211808', 'asn': u'199524'}, 
        {'is_affected': 1, 'path': u'41722 20764 174 3257 29119 31577 211808', 'asn': u'41722'}], 
        'oldhomeas': '174', 'bad_path_segment': u'', 'alarm_id': 10023196, 'newhomeas': '211808', 'type': 0})
