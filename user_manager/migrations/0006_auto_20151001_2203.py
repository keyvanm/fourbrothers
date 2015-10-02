# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0005_userprofile_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='type',
            field=models.CharField(default=b'customer', max_length=15, choices=[(b'customer', b'customer'), (b'technician', b'technician'), (b'manager', b'manager')]),
        ),
    ]
