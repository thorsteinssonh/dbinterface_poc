# -*- coding: utf-8 -*-

from gluon.scheduler import Scheduler
from bulletin import bulletin_schedule_process
# recommended to start separate db for scheduler
sched_db = DAL('sqlite://sched_db.sqlite')
scheduler = Scheduler(sched_db,
                      tasks={'bulletin_schedule_process':bulletin_schedule_process})
