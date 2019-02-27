import os
import time
import schedule


def job():
    os.system('python run.py')


schedule.every().day.at('00:30').do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
