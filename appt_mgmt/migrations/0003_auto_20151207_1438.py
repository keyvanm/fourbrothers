# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appt_mgmt', '0002_auto_20151204_2343'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='loyalty',
            field=models.PositiveSmallIntegerField(default=0, choices=[(0, b'$0'), (10, b'$10'), (20, b'$20'), (30, b'$30'), (40, b'$40'), (50, b'$50')]),
        ),
    ]
