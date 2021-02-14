from helper import *
import schedule
import time

schedule.every().day.at("8:40").do(shedule_job)

while True:
    schedule.run_pending()
    time.sleep(1)
