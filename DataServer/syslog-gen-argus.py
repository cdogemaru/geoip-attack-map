#!/usr/bin/python3

import random, syslog
from const import PORTMAP
from sys import exit
from time import sleep
from dbmgr_test import DBMgr, Routingtree
import json
import numpy as np
def main():


    rt = Routingtree()
    print("Done!")
    dbmgr = DBMgr(rt)
    alarm_list = dbmgr.get_recent_alarm()
    print(alarm_list)

    available_ids = ['10020699', '9963326', '9977031', '9895340', '9925094', '9906670', '9965349', '9886609', '9874603', '10003146', '10002348', '9935580', '9932860', '9988940', '9920383', '9977381', '9917200', '9877484', '9882445',
        '9919499', '9900942', '9921888', '10020269', '9897360', '9872648', '10014496', '9904952', '10001406', '10029271', '9957342', '9889040', '10011372', '9881411', '10038921', '9985868', '9879538', '9889609', '9913594']

    i = 0
    while(1):

        a = alarm_list[i]
        i += 1
        if (i == len(alarm_list)):
            i = 0
        a_id = a[0]
        if not str(a_id) in available_ids:
            continue
        a_info = dbmgr.get_alarm_info_2(a_id)
        data = "^%s|%s|%s" % (a_id, json.dumps(a), json.dumps(a_info))
        print(data)
        syslog.syslog(data)
        sleep(10)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
