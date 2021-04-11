import time
import pickle
import datetime
import MySQLdb
import os
from regular import get_current_week


def init_dir():
    current_dir = os.getcwd()
    result_dir = current_dir + '/result/'
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    basic_dir = result_dir + 'basic/'
    if not os.path.exists(basic_dir):
        os.makedirs(basic_dir)
    pre_dir = result_dir + 'pre/'
    if not os.path.exists(pre_dir):
        os.makedirs(pre_dir)
    after_dir = result_dir + 'after/'
    if not os.path.exists(after_dir):
        os.makedirs(after_dir)
    alarm_info_dir = result_dir + 'alarm_info/'
    if not os.path.exists(alarm_info_dir):
        os.makedirs(alarm_info_dir)
    stat_dir = result_dir + 'stat/'
    if not os.path.exists(stat_dir):
        os.makedirs(stat_dir)


class DBMgr:
    def __init__(self):
        self.conn = MySQLdb.connect(host="localhost", user="maq18", passwd="maqiang1995", db="hijacking", charset="utf8")
        self.cursor = self.conn.cursor()
        self.conn_time = int(time.time())
        
    def is_alive(self):
        if int(time.time()) - self.conn_time > 3600:
            self.conn.ping(True)
            self.cursor = self.conn.cursor()
            self.conn_time = int(time.time())
        
    def get_dist_of_hijacker(self):
        self.is_alive()
        dist_of_hijacker = {}
        sql = """SELECT * FROM alarm WHERE is_hijacking='Y' AND EXISTS (SELECT * FROM signature WHERE signature.alarm_id = alarm.alarm_id) ORDER BY alarm_id"""
        self.cursor.execute(sql)
        alarm_list = self.cursor.fetchall()
        for alarm in alarm_list:
            alarm_type = int(alarm[2])
            if 1<=alarm_type<=4 or 6<=alarm_type<=9:
                hijacker_as = str(alarm[8])
            elif 10<=alarm_type<=13 or 14<=alarm_type<=17:
                hijacker_as = str(alarm[10]).split()[0]
            else:
                hijacker_as = "-1"
            try:
                dist_of_hijacker[hijacker_as] += 1
            except KeyError:
                dist_of_hijacker[hijacker_as] = 1
        return dist_of_hijacker

    def get_nb_of_hijacking_by_week(self):
        self.is_alive()
        sql = """SELECT * FROM alarm WHERE is_hijacking='Y' AND EXISTS (SELECT * FROM signature WHERE signature.alarm_id = alarm.alarm_id) ORDER BY alarm_id"""
        self.cursor.execute(sql)
        alarm_list = self.cursor.fetchall()
        nb_of_hijacking_by_week = {}
        for alarm in alarm_list:
            alarm_time = alarm[1]
            alarm_date = datetime.date.fromtimestamp(alarm_time)
            alarm_weekdate = get_current_week(alarm_date)
            alarm_weekdate_str = "%d-%s-%s" % (alarm_weekdate.year, str(alarm_weekdate.month).zfill(2), str(alarm_weekdate.day).zfill(2))
            try:
                nb_of_hijacking_by_week[alarm_weekdate_str] += 1
            except KeyError:
                nb_of_hijacking_by_week[alarm_weekdate_str] = 1
        res = sorted(nb_of_hijacking_by_week.items(), key=lambda p: (int(p[0].split('-')[0]), int(p[0].split('-')[1]), int(p[0].split('-')[2])))
        return res
    
    def get_nb_of_anomaly_by_week(self):
        self.is_alive()
        sql = """SELECT * FROM alarm WHERE EXISTS (SELECT * FROM signature WHERE signature.alarm_id = alarm.alarm_id) ORDER BY alarm_id"""
        self.cursor.execute(sql)
        alarm_list = self.cursor.fetchall()
        nb_of_anomaly_by_week = {}
        for alarm in alarm_list:
            alarm_time = alarm[1]
            alarm_date = datetime.date.fromtimestamp(alarm_time)
            alarm_weekdate = get_current_week(alarm_date)
            alarm_weekdate_str = "%d-%s-%s" % (alarm_weekdate.year, str(alarm_weekdate.month).zfill(2), str(alarm_weekdate.day).zfill(2))
            try:
                nb_of_anomaly_by_week[alarm_weekdate_str] += 1
            except KeyError:
                nb_of_anomaly_by_week[alarm_weekdate_str] = 1
        res = sorted(nb_of_anomaly_by_week.items(), key=lambda p: (int(p[0].split('-')[0]), int(p[0].split('-')[1]), int(p[0].split('-')[2])))
        return res
            

    def get_recent_alarm(self, max_nb):
        self.is_alive()
        sql = """SELECT alarm_id FROM alarm WHERE is_hijacking='Y' AND EXISTS (SELECT * FROM signature WHERE signature.alarm_id = alarm.alarm_id) ORDER BY alarm_id DESC LIMIT %d""" % max_nb
        self.cursor.execute(sql)
        alarm_list = self.cursor.fetchall()
        return alarm_list

    def get_alarm_info(self, alarm_id):
        self.is_alive()
        alarms = {}
        sql = """SELECT time, type, homeas, oldhomeas, bad_path from alarm WHERE alarm_id = %d""" % alarm_id
        self.cursor.execute(sql)
        elems = self.cursor.fetchone()
        alarm_type = -1
        if 1<=elems[1]<=4 or 6<=elems[1]<=9:
            alarm_type = 0
        elif 10<=elems[1]<=13 or 14<=elems[1]<=17:
            alarm_type = 1
        newhomeas = str(elems[2])
        oldhomeas = str(elems[3])
        bad_path_segment = elems[4]
        vp_info = []
        sql = """SELECT path FROM bgpmon WHERE alarm_id=%d""" % alarm_id
        self.cursor.execute(sql)
        pick_first = 0
        observations = self.cursor.fetchall()
        for path_str in observations:
            path_str = path_str[0]
            if path_str == "":
                continue
            path_list = path_str.split(' ')
            vp_asn = path_list[0]
            is_affected = 0
            if alarm_type == 0 and path_list[-1] == newhomeas:
                is_affected = 1
            elif alarm_type == 1 and bad_path_segment in path_str:
                is_affected = 1
            if alarm_type == 1:
                if pick_first == 0:
                    oldhomeas = path_list[-1]
                    pick_first += 1
            vp_info.append({'asn': vp_asn, 'is_affected': is_affected, 'path': path_str})
        assert(oldhomeas != '0')
        alarms['alarm_id'] = alarm_id
        alarms['time'] = elems[0]
        alarms['type'] = alarm_type
        alarms['oldhomeas'] = oldhomeas
        alarms['newhomeas'] = newhomeas
        alarms['bad_path_segment'] = bad_path_segment
        alarms['vps'] = vp_info
        return alarms

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    init_dir()
    current_dir = os.getcwd()
    result_dir = current_dir + '/result/'
    dbmgr = DBMgr()
    # ============ Note: test get_recent_alarm =========== #
    alarm_list = dbmgr.get_recent_alarm(100)
    file_path = result_dir + 'basic/alarm_id_list.txt'
    fp = open(file_path, 'wb')
    pickle.dump(alarm_list, fp)
    fp.close()
    # ============ Note: test get_alarm_info ============ #
    sampled_alarms = {}
    for alarm in alarm_list:
        alarm_id = alarm[0]
        print(alarm_id)
        alarm_info = dbmgr.get_alarm_info(alarm_id)
        print(alarm_info)
        sampled_alarms[alarm_id] = alarm_info
    file_path = result_dir + 'basic/alarm_info.txt'
    fp = open(file_path, 'wb')
    pickle.dump(sampled_alarms, fp)
    fp.close()
    # ============ Note: test get_nb_of_anomaly_by_week ========== #
    # nb_of_anomaly_by_week = dbmgr.get_nb_of_anomaly_by_week()
    # fp = open(result_dir + 'stat/nb_of_anomaly_by_week.txt', 'wb')
    # pickle.dump(nb_of_anomaly_by_week, fp)
    # fp.close()
    # ============ Note: test get_nb_of_hijacking_by_week ========== #
    # nb_of_hijacking_by_week = dbmgr.get_nb_of_hijacking_by_week()
    # fp = open(result_dir + 'stat/nb_of_hijacking_by_week.txt', 'wb')
    # pickle.dump(nb_of_hijacking_by_week, fp)
    # fp.close()
    # ============ Note: test get_dist_of_hijacker ========== #
    # dist_of_hijacker = dbmgr.get_dist_of_hijacker()
    # fp = open(result_dir + 'stat/dist_of_hijacker.txt', 'wb')
    # pickle.dump(dist_of_hijacker, fp)
    # fp.close()
    dbmgr.close()
