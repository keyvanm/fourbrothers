# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0002_car_engine_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='engine_type',
            field=models.CharField(default=4, max_length=2, choices=[(3, b'V3'), (4, b'V4'), (5, b'V5'), (6, b'V6'), (8, b'V8')]),
        ),
    ]
