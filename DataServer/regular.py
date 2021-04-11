import datetime
import copy


def get_current_week(tm):
    curr_day = tm
    delta_one_day = datetime.timedelta(days=1)
    while curr_day.weekday() != 0:
        curr_day -= delta_one_day
    return curr_day
