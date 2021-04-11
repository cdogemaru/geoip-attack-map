import time
import random
import datetime
import pickle
import os
import regular
import argus_prediction
from argus_prediction import Routingtree
# import MySQLdb


class DBMgr:
    def __init__(self, routing_tree):
        self.rt = routing_tree

    @staticmethod
    def get_nb_of_update():
        stat_dir = os.getcwd() + '/result/stat/'
        file_path = stat_dir + 'updates_per_day_over_one_month.txt'
        if os.path.exists(file_path):
            fp = open(file_path, 'rb')
            updates_per_day = pickle.load(fp)
            fp.close()
        else:
            curr_tm = datetime.date.fromtimestamp(time.time())
            time_delta = datetime.timedelta(days=1)
            times = 30
            nb_of_updates_per_day = {}
            while times != 0:
                curr_tm -= time_delta
                time_str = "%d-%s-%s" % (curr_tm.year, str(curr_tm.month).zfill(2), str(curr_tm.day).zfill(2))
                nb_of_upt = random.randint(120000000, 200000000)
                nb_of_updates_per_day[time_str] = nb_of_upt
                times -= 1
            updates_per_day = sorted(nb_of_updates_per_day.items(), key=lambda p: (int(p[0].split('-')[0]), int(p[0].split('-')[1]), int(p[0].split('-')[2])))
            fp = open(file_path, 'wb')
            pickle.dump(updates_per_day, fp)
            fp.close()
        return updates_per_day
    
    @staticmethod
    def get_dist_of_hijacker():
        result_dir = os.getcwd() + '/result/'
        fp = open(result_dir + 'stat/dist_of_hijacker.txt', 'rb')
        dist_of_hijacker = pickle.load(fp)
        fp.close()
        return dist_of_hijacker

    @staticmethod
    def get_nb_of_hijacking_by_week():
        result_dir = os.getcwd() + '/result/'
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        stat_dir = result_dir + 'stat/'
        if not os.path.exists(stat_dir):
            os.makedirs(stat_dir)
        file_path = stat_dir + 'nb_of_hijacking_by_week.txt'
        if os.path.exists(file_path):
            fp = open(file_path, 'rb')
            nb_of_hijacking_by_week = pickle.load(fp)
            fp.close()
        else:
            nb_of_hijacking_by_week = {}
            start_date = datetime.date(year=2012, month=1, day=8)
            end_date = datetime.date(year=2021, month=4, day=1)
            delta_one_day = datetime.timedelta(days=1)
            curr_date = start_date
            previous_weekday = datetime.date(year=2000, month=1, day=8)
            while curr_date < end_date:
                nb_of_oa_hijacking = random.randint(2, 6)
                nb_of_aa_hijacking = random.randint(10, 15)
                nb_of_pa_hijacking = random.randint(16, 20)
                nb_of_all = nb_of_oa_hijacking + nb_of_aa_hijacking + nb_of_pa_hijacking
                weekday = regular.get_current_week(curr_date)
                if previous_weekday != weekday:
                    time_str = "%s-%s-%s" % (str(weekday.year), str(weekday.month).zfill(2), str(weekday.day).zfill(2))
                    nb_of_hijacking_by_week[time_str] = {"OA": nb_of_oa_hijacking, "AA": nb_of_aa_hijacking, "PA": nb_of_pa_hijacking,
                                                         "All": nb_of_all}
                    previous_weekday = weekday
                curr_date += delta_one_day
            res = sorted(nb_of_hijacking_by_week.items(),
                         key=lambda p: (int(p[0].split('-')[0]), int(p[0].split('-')[1]), int(p[0].split('-')[2])))
            fp = open(file_path, 'wb')
            pickle.dump(nb_of_hijacking_by_week, fp)
            fp.close()
        return nb_of_hijacking_by_week

    @staticmethod
    def get_nb_of_anomaly_by_week():
        result_dir = os.getcwd() + '/result/'
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        stat_dir = result_dir + 'stat/'
        if not os.path.exists(stat_dir):
            os.makedirs(stat_dir)
        file_path = stat_dir + 'nb_of_anomaly_by_week.txt'
        if os.path.exists(file_path):
            fp = open(file_path, 'rb')
            nb_of_anomaly_by_week = pickle.load(fp)
            fp.close()
        else:
            nb_of_anomaly_by_week = {}
            start_date = datetime.date(year=2012, month=1, day=8)
            end_date = datetime.date(year=2021, month=4, day=1)
            delta_one_day = datetime.timedelta(days=1)
            curr_date = start_date
            previous_weekday = datetime.date(year=2000, month=1, day=8)
            while curr_date < end_date:
                nb_of_oa_anomaly = random.randint(10, 12)
                nb_of_aa_anomaly = random.randint(20, 30)
                nb_of_pa_anomaly = random.randint(31, 45)
                nb_of_all = nb_of_oa_anomaly + nb_of_aa_anomaly + nb_of_pa_anomaly
                weekday = regular.get_current_week(curr_date)
                if previous_weekday != weekday:
                    time_str = "%s-%s-%s" % (str(weekday.year), str(weekday.month).zfill(2), str(weekday.day).zfill(2))
                    nb_of_anomaly_by_week[time_str] = {"OA": nb_of_oa_anomaly, "AA": nb_of_aa_anomaly, "PA": nb_of_pa_anomaly,
                                                       "All": nb_of_all}
                    previous_weekday = weekday
                curr_date += delta_one_day
            res = sorted(nb_of_anomaly_by_week.items(), key=lambda p: (int(p[0].split('-')[0]), int(p[0].split('-')[1]), int(p[0].split('-')[2])))
            fp = open(file_path, 'wb')
            pickle.dump(res, fp)
            fp.close()
        return nb_of_anomaly_by_week

    @staticmethod
    def get_recent_alarm():
        current_dir = os.getcwd()
        fp = open(current_dir + '/result/basic/alarm_id_list.txt', 'rb')
        alarm_list = pickle.load(fp, encoding='iso-8859-1')
        fp.close()
        return alarm_list

    @staticmethod
    def get_alarm_info(alarm_id):
        current_dir = os.getcwd()
        fp = open(current_dir + '/result/basic/alarm_info.txt', 'rb')
        alarms = pickle.load(fp, encoding='iso-8859-1')
        fp.close()
        return alarms[alarm_id]

    def get_alarm_info_2(self, alarm_id):
        result_dir = os.getcwd() + '/result/'
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        alarm_info_dir = result_dir + 'alarm_info/'
        if not os.path.exists(alarm_info_dir):
            os.makedirs(alarm_info_dir)
        file_path = alarm_info_dir + str(alarm_id) + '.txt'
        if os.path.exists(file_path):
            fp = open(file_path, 'rb')
            alarms = pickle.load(fp)
            fp.close()
        else:
            alarms = DBMgr.get_alarm_info(alarm_id)
            previous_path_set = self.get_previous_path_set(alarm_id)
            vp_info = alarms['vps']
            vp_asn_list = []
            pos_list = []
            for i in range(len(vp_info)):
                vp_asn_list.append(vp_info[i]['asn'])
                pos_list.append(i)
            for elem in previous_path_set:
                if elem['asn'] in vp_asn_list:
                    idx = vp_asn_list.index(elem['asn'])
                    pos = pos_list[idx]
                    vp_info[pos]['before_path'] = elem['path']
            for elem in vp_info:
                if elem.get('before_path') is None:
                    elem['before_path'] = ""
            alarms['vps'] = vp_info
            fp = open(file_path, 'wb')
            pickle.dump(alarms, fp)
            fp.close()
        return alarms

    def get_previous_path_set(self, alarm_id):
        tmp_path = os.getcwd()
        result_dir = tmp_path + '/result/'
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        pre_result_dir = result_dir +'pre/'
        if not os.path.exists(pre_result_dir):
            os.makedirs(pre_result_dir)
        file_path = pre_result_dir + str(alarm_id) + '.txt'
        if not os.path.exists(file_path):
            alarm_info = DBMgr.get_alarm_info(alarm_id)
            pre_path_set = self.rt.first_epoch(alarm_info)
            fp = open(file_path, 'wb')
            pickle.dump(pre_path_set, fp)
            fp.close()
        else:
            fp = open(file_path, 'rb')
            pre_path_set = pickle.load(fp)
            fp.close()
        return pre_path_set

    def get_after_path_set(self, alarm_id):
        tmp_path = os.getcwd()
        result_dir = tmp_path + '/result/'
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        after_result_dir = result_dir +'after/'
        if not os.path.exists(after_result_dir):
            os.makedirs(after_result_dir)
        file_path = after_result_dir + str(alarm_id) + '.txt'
        if not os.path.exists(file_path):
            alarm_info = DBMgr.get_alarm_info(alarm_id)
            after_path_set = self.rt.second_epoch(alarm_info)
            fp = open(file_path, 'wb')
            pickle.dump(after_path_set, fp)
            fp.close()
        else:
            fp = open(file_path, 'rb')
            after_path_set = pickle.load(fp)
            fp.close()
        return after_path_set

    def close(self):
        pass


if __name__ == "__main__":
    print("Initializing routing tree......")
    rt = Routingtree()
    print("Done!")
    dbmgr = DBMgr(rt)
    alarm_list = dbmgr.get_recent_alarm()
    nb_of_error_case = 0
    for alarm in alarm_list:
        alarm_id = alarm[0]
        print(alarm_id)
        alarm_info = dbmgr.get_alarm_info(alarm_id)
        previous_path_set = dbmgr.get_previous_path_set(alarm_id)
        print(len(previous_path_set))
        after_path_set = dbmgr.get_after_path_set(alarm_id)
        print(len(after_path_set))
        # print(after_path_set)
    # nb_of_anomaly_by_week = dbmgr.get_nb_of_anomaly_by_week()
    # print(nb_of_anomaly_by_week)
    # nb_of_hijacking_by_week = dbmgr.get_nb_of_hijacking_by_week()
    # print(nb_of_hijacking_by_week)
    # dist_of_hijacker = dbmgr.get_dist_of_hijacker()
    # print(dist_of_hijacker)
    dbmgr.close()
