# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appt_mgmt', '0003_auto_20151001_2203'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='technicians',
            new_name='technician',
        ),
    ]
