from django_cron import CronJobBase, Schedule
from sales.models import DoctorDetail

class DoctorJob(CronJobBase) :
    RUN_EVERY_MINS = 10

    schedule = Schedule(run_every_mins = RUN_EVERY_MINS)

    code = 'sales.my_cron_job'

    def do(self) :
        print("Running cron job...")