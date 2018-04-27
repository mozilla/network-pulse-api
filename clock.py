import threading
from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()


@sched.scheduled_job('interval', minutes=15)
def timed_job():
    from pulseapi.utility import contributions_data
    t = threading.Thread(
        target=contributions_data.run,
        daemon=True,
    )
    t.start()

sched.start()
