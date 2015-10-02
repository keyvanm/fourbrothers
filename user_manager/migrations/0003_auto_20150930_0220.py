# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0002_auto_20150920_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('next_scheduled_time', models.DateField()),
                ('time_slot', models.CharField(blank=True, max_length=10, choices=[(b'8am', b'8 - 11 AM'), (b'11am', b'11 AM - 2 PM'), (b'2pm', b'2 - 5 PM'), (b'5pm', b'5 - 8 PM')])),
                ('address', models.OneToOneField(to='user_manager.Address')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='type',
        ),
    ]
