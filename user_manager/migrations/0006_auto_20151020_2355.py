# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0005_auto_20151020_2103'),
    ]

    operations = [
        migrations.AlterField(
            model_name='car',
            name='engine_type',
            field=models.CharField(default=4, max_length=2, choices=[(b'v3', b'V3'), (b'v4', b'V4'), (b'v5', b'V5'), (b'v6', b'V6'), (b'v8', b'V8')]),
        ),
    ]
