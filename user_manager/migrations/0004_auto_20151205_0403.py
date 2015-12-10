# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0003_auto_20151205_0347'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='state',
            field=models.CharField(default=b'Ontario', max_length=200, verbose_name=b'Province', choices=[(b'Ontario', b'Ontario')]),
        ),
    ]
