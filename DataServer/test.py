import pickle
import os


def remove_alarm_id():
	result_dir = os.getcwd() + '/result/'
	basic_dir = result_dir + 'basic/'
	pre_path_dir = result_dir + 'pre/'
	file_path = basic_dir + 'alarm_id_list.txt'
	fp = open(file_path, 'rb')
	alarm_id_list = pickle.load(fp)
	fp.close()
	new_alarm_id_list = []
	nb_of_case_with_no_pre_path = 0
	for elem in alarm_id_list:
		alarm_id = elem[0]
		file_path = pre_path_dir + str(alarm_id) + '.txt'
		fp = open(file_path, 'rb')
		pre_path_set = pickle.load(fp)
		fp.close()
		if len(pre_path_set) >= 2:
			new_alarm_id_list.append((alarm_id,))
	return new_alarm_id_list


if __name__ == "__main__":
	current_dir = os.getcwd()
	new_alarm_id_list = remove_alarm_id()
	fp = open(current_dir + '/alarm_id_list.txt', 'wb')
	pickle.dump(new_alarm_id_list, fp)
	fp.close()
