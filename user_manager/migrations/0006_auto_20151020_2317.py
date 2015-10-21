# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0005_auto_20151020_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='loyalty_points',
            field=models.PositiveIntegerField(default=0, validators=[b'^[0-9]*$']),
        ),
    ]
