#!/usr/bin/python3

import random, syslog
from const import PORTMAP
from sys import exit
from time import sleep
from argus_show.dbmgr_test import DBMgr
import json
import numpy as np
def main():


    dbmgr = DBMgr()
    alarm_list = dbmgr.get_recent_alarm()
    # for alarm in alarm_list[:5]:
    #     print(alarm)
    #     alarm_id = alarm[0]
    #     print(alarm_id)
    #     alarm_info = dbmgr.get_alarm_info(alarm_id)
    #     print(alarm_info)

    # while(True):
    i = 0
    while(1):
    # for i in range(3,4):

        a = alarm_list[i]
        i += 1
        if (i == len(alarm_list)):
            i = 0
        a_id = a[0]
        a_info = dbmgr.get_alarm_info(a_id)
        data = "^%s|%s|%s" % (a_id, json.dumps(a), json.dumps(a_info))
        print(data)
        syslog.syslog(data)
        sleep(10)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
