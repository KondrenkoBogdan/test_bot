from helper import *
import schedule
import time

schedule.every().day.at("10:36").do(shedule_job)

while True:
    schedule.run_pending()
    time.sleep(1)
