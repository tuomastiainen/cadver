from checker.celery import app
import os
from django.conf import settings
from creocheck.models import CheckTemplate
import traceback
if os.name == 'nt':
    from creocheck.creo import PythonCreoConnection


from time import sleep
import json


import random


from creocheck.creo import MassPropChecker, ModelTreeChecker, RegenChecker, MacroRunner, SaveMetaData, SleepOneSecond

check_classes = {'MassPropChecker': MassPropChecker,
                 'ModelTreeChecker': ModelTreeChecker,
                 'RegenChecker': RegenChecker,
                 'MacroRunner': MacroRunner,
                 'SaveMetaData': SaveMetaData,
                 'SleepOneSecond': SleepOneSecond,
                 }


@app.task
def run_checktask(task_pk):
    from creocheck.models import CheckTask
    from creocheck.models import Check

    checktask = CheckTask.objects.get(pk=task_pk)
    print("Running checks")
    checktask.set_progress(0, 1)
    checks_n = CheckTemplate.objects.filter(
        assignment=checktask.assignment).count()

    for index, checktemplate in enumerate(CheckTemplate.objects.filter(assignment=checktask.assignment)):
        # create and run checks based on each checktemplate connected to selected
        c = Check.objects.create(template=checktemplate, task=checktask)

        try:
            f = check_classes.get(c.template.check_func)
            if not f:
                raise Exception(
                    "Check function {} not defined".format(c.template.check_func))
            print("Running {}".format(f.__name__))
            check_instance = f(check_object=c, checktemplate=checktemplate)
            c.passed = check_instance.check_result()
        except:
            traceback.print_exc()
            c.status = traceback.format_exc()
            c.passed = False

        c.save()
        checktask.set_progress(index + 1, checks_n)

    checktask.passed = True
    for i in Check.objects.filter(task=checktask):
        if i.passed == False:
            checktask.passed = False

    checktask.save()
    checktask.set_progress(1, 1)

    # add a small delay to prevent problems with instantly making calls to the
    # VBAPI again
    sleep(1)
