import os
import time
import schedule


def job():
    os.system('python run.py')


def job2():
    os.system('python run_tracer.py')


schedule.every().day.at('00:30').do(job)
schedule.every(30).minutes.do(job2)

while True:
    schedule.run_pending()
    time.sleep(1)
