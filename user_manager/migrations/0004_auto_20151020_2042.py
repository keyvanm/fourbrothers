# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0003_auto_20151020_2039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='loyalty_points',
            field=models.PositiveIntegerField(default=0, choices=[(0, b'$0'), (10, b'$10'), (20, b'$20'), (30, b'$30'), (40, b'$40'), (50, b'$50')]),
        ),
    ]
