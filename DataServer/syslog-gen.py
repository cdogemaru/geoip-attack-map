#!/usr/bin/python3

import random, syslog
from const import PORTMAP
from sys import exit
from time import sleep
from argus_show.dbmgr_test import DBMgr
import json

def main():


    # dbmgr = DBMgr()
    # alarm_list = dbmgr.get_recent_alarm()
    # # for alarm in alarm_list[:5]:
    # #     print(alarm)
    # #     alarm_id = alarm[0]
    # #     print(alarm_id)
    # #     alarm_info = dbmgr.get_alarm_info(alarm_id)
    # #     print(alarm_info)

    # # while(True):
    # for i in range(5):
    #     a = alarm_list[i]
    #     a_id = a[0]
    #     a_info = dbmgr.get_alarm_info(a_id)
    #     data = "%s|%s|%s" % (a_id, json.dumps(a), json.dumps(a_info))
    #     print(data)
    #     syslog.syslog(data)
    #     sleep(1)


    port_list = []
    type_attack_list = []

    for port in PORTMAP:
        port_list.append(port)
        type_attack_list.append(PORTMAP[port])

    # while True:
    for i in range(5):
        port = random.choice(port_list)
        type_attack = random.choice(type_attack_list)
        cve_attack = 'CVE:{}:{}'.format(
                                random.randrange(1,2000),
                                random.randrange(100,1000)
                                )

        rand_data = '{}.{}.{}.{},{}.{}.{}.{},{},{},{},{}'.format(
                                                            random.randrange(1, 256),
                                                            random.randrange(1, 256),
                                                            random.randrange(1, 256),
                                                            random.randrange(1, 256),
                                                            random.randrange(1, 256),
                                                            random.randrange(1, 256),
                                                            random.randrange(1, 256),
                                                            random.randrange(1, 256),
                                                            port,
                                                            port,
                                                            type_attack,
                                                            cve_attack
                                                            )

        syslog.syslog(rand_data)
        print(rand_data)
        sleep(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
