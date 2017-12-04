from django.db import models

import traceback
from django.conf import settings


class UploadFile(models.Model):
    display_name = models.CharField(max_length=150, blank=True, null=True)
    file = models.FileField(upload_to='files')
    metadata = models.TextField(blank=True, null=True)

    def fileLink(self):
        if self.file:
            return '<a href="' + str(self.File.url) + '">' + 'NameOfFileGoesHere' + '</a>'
        else:
            return '<a href="''"></a>'

    fileLink.allow_tags = True
    fileLink.short_description = "File Link"

    def __str__(self):
        return "{} - {}".format(self.pk, self.file.name)


class MacroTemplate(models.Model):
    name = models.CharField(max_length=50)
    macro = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.pk, self.name)







class AssignmentCollection(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return "{}".format(self.name)



class Assignment(models.Model):

    order = models.SmallIntegerField(default=0)

    collection = models.ForeignKey(AssignmentCollection)

    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    correct_file = models.FileField(upload_to='files')

    def __str__(self):
        return "{} - {}".format(self.pk, self.name)


    class Meta:
        ordering = ['order']


class CheckTemplate(models.Model):
    assignment = models.ForeignKey(Assignment)
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)

    CHECK_FUNCS = (
            ('MassPropChecker', 'MassPropChecker'),
            ('ModelTreeChecker', 'ModelTreeChecker'),
            ('RegenChecker', 'RegenChecker'),
            ('MacroRunner', 'MacroRunner'),
            ('SaveMetadata', 'SaveMetadata'),
            ('SleepOneSecond', 'SleepOneSecond'),
            )

    check_func = models.CharField(max_length=50, choices=CHECK_FUNCS)

    # check parameters as JSON
    checkparams = models.TextField(blank=True, null=True)

    def __str__(self):
        return "{} - {}".format(self.pk, self.name)


from django.contrib.auth.models import User

from creocheck.tasks import run_checktask


class CheckUser(models.Model):

    user_id = models.CharField(max_length=30)


    @property
    def passed(self):
        return CheckTask.objects.filter(user=self, passed=True).exists()


    @property
    def attempts(self):
        return CheckTask.objects.filter(user=self).count()



    def __str__(self):
        return "{}".format(self.user_id)


class CheckTask(models.Model):

    created = models.DateTimeField(auto_now_add=True, null=True)

    user = models.ForeignKey(CheckUser, null=True, blank=True)

    assignment = models.ForeignKey(Assignment)
    file = models.ForeignKey(UploadFile)

    progress = models.FloatField(default=0)
    done = models.BooleanField(default=False)
    error = models.BooleanField(default=False)
    passed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created']

    def run(self):
        run_checktask.delay(self.pk)

    def set_progress(self, progress, max_progress):
        self.progress = float(progress) / float(max_progress)
        if progress == max_progress:
            self.done = True
        self.save()

    def get_checks(self):
        return Check.objects.filter(task=self)

    def get_status(self):

        if self.error:
            return "ERROR"

        if self.done:
            return "DONE"

        if self.progress == 0:
            return "PENDING"

        if self.progress > 0:
            return "IN PROGRESS"

    def __str__(self):
        return "{}".format(self.pk)


    class Meta:
        ordering = ['-passed', '-created']


class Check(models.Model):
    template = models.ForeignKey(CheckTemplate)
    task = models.ForeignKey(CheckTask)
    status = models.TextField(blank=True, null=True)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return "{}".format(self.template.check_func)


class CheckLogEvent(models.Model):

    check_object = models.ForeignKey(Check)
    created = models.DateTimeField(auto_now_add=True, null=True)
    text = models.CharField(max_length=300)

    def __str__(self):
        return "{} - {}: {}".format(self.created, self.check_object.template.name, self.text)
