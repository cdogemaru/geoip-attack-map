# coding=utf-8
import time
import pickle
# import MySQLdb

class DBMgr:
    def __init__(self):
        self.init = 1
        # self.conn = MySQLdb.connect(host="localhost", user="maq18", passwd="maqiang1995", db="hijacking", charset="utf8")
        # self.cursor = self.conn.cursor()
        # self.conn_time = int(time.time())

    def get_recent_alarm(self):
        fp = open('./argus_show/alarm_id_list.txt', 'rb')
        alarm_list = pickle.load(fp, encoding="latin1")
        fp.close()
        return alarm_list

    def get_alarm_info(self, alarm_id):
        fp = open('./argus_show/alarm_info.txt', 'rb')
        alarms = pickle.load(fp, encoding="latin1")
        fp.close()
        return alarms[alarm_id]

    def close(self):
        self.init = 0
        # self.cursor.close()
        # self.conn.close()


if __name__ == "__main__":
    dbmgr = DBMgr()
    alarm_list = dbmgr.get_recent_alarm()
    for alarm in alarm_list:
        alarm_id = alarm[0]
        print(alarm_id)
        alarm_info = dbmgr.get_alarm_info(alarm_id)
        print(alarm_info)
    dbmgr.close()
