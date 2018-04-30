import threading
import os

from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pulseapi.settings")

@sched.scheduled_job('interval', minutes=30)
def timed_job():
    from pulseapi.utility import contributions_data
    t = threading.Thread(
        target=contributions_data.run,
        daemon=True,
    )
    t.start()

sched.start()
