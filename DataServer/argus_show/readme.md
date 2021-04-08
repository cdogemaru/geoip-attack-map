# 简介
本目录下有两个代码文件，其中dbmgr.py是正式上线使用时的版本（从数据库里读取），dbmgr_test.py是测试版本（从本目录的缓存文件中读取），当前只介绍dbmgr_test的使用方式

## dbmgr_test
get_recent_alarm(self): 返回一个list，包含了每一个劫持告警信息的id，利用该id可进一步取得该告警的其他详细信息

get_alarm_info(self, alarm_id): 取alarm_id对应的告警的详细信息，返回类型为字典，格式如下：
{'alarm_id':alarm_id(int类型), 'type': alarm_type(int类型，0表示origin劫持，1表示一跳链路劫持), 'oldhomeas': oldhomeas(原始origin AS号，即victim，str类型), 'newhomeas': newhomeas(新的origin AS号，即attacker，str类型), 'bad_path_segment': bad_path_segment(如为1类型劫持，则表示可以一跳链路，str类型，例如"3356 131071"), 'vps': vp_info(每个vp的信息，list格式)}

其中vp_info的格式如下
vp_info = [{'asn': asn(str格式), 'is_affected': is_affected(是否被感染，int类型，0/1), 'path': path(该vp的路径，str格式，如"3356 3549 131071")}, ...]
