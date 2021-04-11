import time
import pickle
import MySQLdb

class DBMgr:
    def __init__(self):
        self.conn = MySQLdb.connect(host="localhost", user="maq18", passwd="maqiang1995", db="hijacking", charset="utf8")
        self.cursor = self.conn.cursor()
        self.conn_time = int(time.time())

    def get_recent_alarm(self, max_nb):
        if int(time.time()) - self.conn_time > 3600:
            self.conn.ping(True)
            self.cursor = self.conn.cursor()
            self.conn_time = int(time.time())
        sql = """SELECT * FROM alarm WHERE is_hijacking='Y' ORDER BY alarm_id DESC LIMIT %d""" % max_nb
        self.cursor.execute(sql)
        alarm_list = self.cursor.fetchall()
        return alarm_list

    def get_alarm_info(self, alarm_id):
        if int(time.time()) - self.conn_time > 3600:
            self.conn.ping(True)
            self.cursor = self.conn.cursor()
            self.conn_time = int(time.time())
        alarms = {}
        sql = """SELECT type, homeas, oldhomeas, bad_path from alarm WHERE alarm_id = %d""" % alarm_id
        self.cursor.execute(sql)
        elems = self.cursor.fetchone()
        alarm_type = -1
        if 1<=elems[0]<=4 or 6<=elems[0]<=9:
            alarm_type = 0
        elif 10<=elems[0]<=13 or 14<=elems[0]<=17:
            alarm_type = 1
        newhomeas = str(elems[1])
        oldhomeas = str(elems[2])
        bad_path_segment = elems[3]
        vp_info = []
        sql = """SELECT path FROM bgpmon WHERE alarm_id=%d""" % alarm_id
        self.cursor.execute(sql)
        observations = self.cursor.fetchall()
        for path_str in observations:
            path_str = path_str[0]
            if path_str == "":
                continue
            path_list = path_str.split()
            vp_asn = path_list[0]
            is_affected = 0
            if alarm_type == 0 and path_list[-1] == newhomeas:
                is_affected = 1
            elif alarm_type == 1 and bad_path_segment in path_str:
                is_affected = 1
            vp_info.append({'asn': vp_asn, 'is_affected': is_affected, 'path':path_str})
        alarms['alarm_id'] = alarm_id
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
    dbmgr = DBMgr()
    alarm_list = dbmgr.get_recent_alarm(10)
    fp = open('./alarm_id_list.txt', 'wb')
    pickle.dump(alarm_list, fp)
    fp.close()
    sampled_alarms = {}
    for alarm in alarm_list:
        alarm_id = alarm[0]
        # print(alarm_id)
        alarm_info = dbmgr.get_alarm_info(alarm_id)
        # print(alarm_info)
        sampled_alarms[alarm_id] = alarm_info
    fp = open('./alarm_info.txt', 'wb')
    pickle.dump(sampled_alarms, fp)
    fp.close()
    dbmgr.close()
