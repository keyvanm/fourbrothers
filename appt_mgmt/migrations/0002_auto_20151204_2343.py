# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0001_initial'),
        ('appt_mgmt', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('appt_fee', models.DecimalField(max_digits=10, decimal_places=2)),
                ('gratuity', models.PositiveSmallIntegerField(default=10, choices=[(0, b'0%'), (5, b'5%'), (10, b'10%'), (15, b'15%'), (20, b'20%')])),
                ('loyalty', models.PositiveSmallIntegerField(choices=[(0, b'$0'), (10, b'$10'), (20, b'$20'), (30, b'$30'), (40, b'$40'), (50, b'$50')])),
            ],
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='gratuity',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='paid',
        ),
        migrations.AddField(
            model_name='invoice',
            name='appointment',
            field=models.OneToOneField(to='appt_mgmt.Appointment'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='promo',
            field=models.ForeignKey(blank=True, to='user_manager.Promotion', null=True),
        ),
    ]
