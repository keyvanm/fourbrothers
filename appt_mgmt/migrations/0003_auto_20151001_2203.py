# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appt_mgmt', '0002_auto_20151001_0051'),
    ]

    operations = [
        migrations.RenameField(
            model_name='appointment',
            old_name='technician',
            new_name='technicians',
        ),
    ]
