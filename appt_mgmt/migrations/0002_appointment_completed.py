# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appt_mgmt', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='completed',
            field=models.BooleanField(default=False),
        ),
    ]
