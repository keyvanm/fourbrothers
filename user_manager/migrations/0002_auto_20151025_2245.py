# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='engine_type',
            field=models.CharField(default=b'4', max_length=2, choices=[(b'3', b'V3'), (b'4', b'V4'), (b'5', b'V5'), (b'6', b'V6'), (b'8', b'V8')]),
        ),
        migrations.AlterField(
            model_name='parkinglocation',
            name='name',
            field=models.CharField(max_length=200, verbose_name=b'Nickname', blank=True),
        ),
    ]
