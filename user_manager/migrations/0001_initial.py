# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django.core.validators
import django_extensions.db.fields
import user_manager.models.promo


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('address1', models.CharField(max_length=255, verbose_name=b'Street Address')),
                ('address2', models.CharField(max_length=255, verbose_name=b'Apt/Suite/Bldg', blank=True)),
                ('city', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=200, verbose_name=b'State/Province')),
                ('postal_code', models.CharField(max_length=20, verbose_name=b'ZIP/Postal Code')),
                ('country', models.CharField(default=b'Canada', max_length=200)),
            ],
            options={
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('name', models.CharField(unique=True, max_length=200)),
                ('address', models.OneToOneField(to='user_manager.Address')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='BuildingPreScheduledTimeSlot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('date', models.DateField()),
                ('time_slot', models.CharField(blank=True, max_length=10, choices=[(b'8am', b'8 - 11 AM'), (b'11am', b'11 AM - 2 PM'), (b'2pm', b'2 - 5 PM'), (b'5pm', b'5 - 8 PM')])),
                ('building', models.ForeignKey(related_name='available_slots', to='user_manager.Building')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('deleted', models.BooleanField(default=False)),
                ('make', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('year', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(2050), django.core.validators.MinValueValidator(1887)])),
                ('color', models.CharField(max_length=50)),
                ('plate', models.CharField(max_length=15)),
                ('mileage', models.PositiveIntegerField(null=True, blank=True)),
                ('engine_type', models.CharField(default=4, max_length=2, choices=[(3, b'V3'), (4, b'V4'), (5, b'V5'), (6, b'V6'), (8, b'V8')])),
                ('additional_info', models.TextField(blank=True)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='CreditCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('card_id', models.CharField(max_length=50)),
                ('fingerprint', models.CharField(max_length=50)),
                ('last_4_digits', models.CharField(max_length=4)),
                ('user', models.ForeignKey(related_name='creditcards', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ParkingLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('name', models.CharField(max_length=200, verbose_name=b'Nickname')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='Promotion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('code', models.CharField(unique=True, max_length=20)),
                ('type', models.CharField(max_length=50, choices=[(b'percent', b'percent'), (b'amount', b'amount'), (b'first-percent', b'first-percent'), (b'first-amount', b'first-amount')])),
                ('discount', models.PositiveSmallIntegerField()),
                ('expiry_date', models.DateField(default=user_manager.models.promo.a_month_from_now)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_customer_id', models.CharField(max_length=50, blank=True)),
                ('type', models.CharField(default=b'customer', max_length=15, choices=[(b'customer', b'customer'), (b'technician', b'technician'), (b'manager', b'manager')])),
                ('loyalty_points', models.PositiveIntegerField(default=0)),
                ('phone_number', models.CharField(max_length=20, blank=True)),
                ('inviter', models.ForeignKey(related_name='invitees', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('promos_used', models.ManyToManyField(to='user_manager.Promotion', blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PrivateParkingLocation',
            fields=[
                ('parkinglocation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='user_manager.ParkingLocation')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=('user_manager.parkinglocation',),
        ),
        migrations.CreateModel(
            name='SharedParkingLocation',
            fields=[
                ('parkinglocation_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='user_manager.ParkingLocation')),
                ('building', models.ForeignKey(to='user_manager.Building')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=('user_manager.parkinglocation',),
        ),
        migrations.AddField(
            model_name='parkinglocation',
            name='address',
            field=models.OneToOneField(related_name='parkinglocation_set', to='user_manager.Address'),
        ),
        migrations.AddField(
            model_name='parkinglocation',
            name='owner',
            field=models.ForeignKey(related_name='parkinglocation_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
