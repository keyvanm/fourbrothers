# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appt_mgmt', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='gratuity',
        ),
        migrations.AddField(
            model_name='appointment',
            name='gratuity',
            field=models.PositiveSmallIntegerField(default=10, choices=[(0, b'0%'), (5, b'5%'), (10, b'10%'), (15, b'15%'), (20, b'20%')]),
        ),
    ]
