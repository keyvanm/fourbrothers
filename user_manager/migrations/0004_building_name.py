# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0003_auto_20150930_0220'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='name',
            field=models.CharField(default='a', max_length=200),
            preserve_default=False,
        ),
    ]
