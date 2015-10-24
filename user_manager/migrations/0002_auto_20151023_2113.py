# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(max_length=200, choices=[(b'Downtown Toronto', b'Downtown Toronto'), (b'East York', b'East York'), (b'Etobicoke', b'Etobicoke'), (b'Markham', b'Markham'), (b'North Toronto', b'North Toronto'), (b'North York', b'North York'), (b'Scarborough', b'Scarborough'), (b'Thornhill', b'Thornhill'), (b'Vaughan', b'Vaughan'), (b'York', b'York')]),
        ),
    ]
