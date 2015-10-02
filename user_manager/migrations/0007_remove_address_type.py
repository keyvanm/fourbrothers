# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0006_auto_20151001_2203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='type',
        ),
    ]
