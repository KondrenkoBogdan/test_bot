from helper import *
import schedule
import time

schedule.every(2).seconds.do(schedule_print)

while True:
    schedule.run_pending()
    time.sleep(1)
