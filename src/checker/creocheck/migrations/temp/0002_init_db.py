# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback

from django.db import migrations, models

from django.core.files import File
import io
import json

from django.contrib.auth.models import User

def init_db(apps, schema_editor):
    return
    Assignment = apps.get_model("creocheck", "Assignment")
    CheckTask= apps.get_model("creocheck", "CheckTask")
    CheckTemplate= apps.get_model("creocheck", "CheckTemplate")

    f = File(io.StringIO("TESTI"))
    Assignment.objects.all().delete()
    a = Assignment.objects.create(name="Test assignment", description="Testi", correct_file=f)
    CheckTemplate.objects.all().delete()
    User.objects.create_superuser(username='tuomas', password='tuomastuomas', email='tuomas@tuomas.com')




class Migration(migrations.Migration):

    dependencies = [
        ('creocheck', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(init_db)
    ]
