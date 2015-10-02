# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('appt_mgmt', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='technician',
            field=models.ManyToManyField(related_name='assigned_appts', to=settings.AUTH_USER_MODEL, blank=True),
        ),
    ]
