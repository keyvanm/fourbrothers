# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('user_manager', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('canceled', models.BooleanField(default=False)),
                ('date', models.DateField()),
                ('time_slot', models.CharField(max_length=10, choices=[(b'8am', b'8 - 11 AM'), (b'11am', b'11 AM - 2 PM'), (b'2pm', b'2 - 5 PM'), (b'5pm', b'5 - 8 PM')])),
                ('paid', models.BooleanField(default=False)),
                ('address', models.ForeignKey(to='user_manager.ParkingLocation')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('picture', models.ImageField(upload_to=b'service-pics', blank=True)),
                ('fee', models.DecimalField(max_digits=10, decimal_places=2)),
                ('duration', models.DurationField()),
                ('gratuity', models.PositiveSmallIntegerField(default=10, choices=[(0, b'0%'), (5, b'5%'), (10, b'10%'), (15, b'15%'), (20, b'20%')])),
            ],
        ),
        migrations.CreateModel(
            name='ServicedCar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('appointment', models.ForeignKey(to='appt_mgmt.Appointment')),
                ('car', models.ForeignKey(to='user_manager.Car')),
                ('services', models.ManyToManyField(to='appt_mgmt.Service')),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='cars',
            field=models.ManyToManyField(to='user_manager.Car', through='appt_mgmt.ServicedCar'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='technician',
            field=models.ManyToManyField(related_name='assigned_appts', to=settings.AUTH_USER_MODEL, blank=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='user',
            field=models.ForeignKey(related_name='appointments', to=settings.AUTH_USER_MODEL),
        ),
    ]
