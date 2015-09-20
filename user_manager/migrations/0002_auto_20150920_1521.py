# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='building_type',
            field=models.CharField(default='home', max_length=20, choices=[(b'house', b'house'), (b'building', b'building')]),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='address',
            name='type',
            field=models.CharField(max_length=20, choices=[(b'home', b'home'), (b'work', b'work')]),
        ),
    ]
