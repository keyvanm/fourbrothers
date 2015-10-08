# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appt_mgmt', '0002_auto_20151007_1510'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='additional_info',
            field=models.TextField(blank=True),
        ),
    ]
