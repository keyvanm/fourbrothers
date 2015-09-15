# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_extensions.db.fields
import django.utils.timezone
from django.conf import settings
import django.core.validators


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
                ('type', models.CharField(max_length=20, choices=[(b'house', b'house'), (b'building', b'building')])),
                ('primary', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('phone_number', models.CharField(max_length=20, blank=True)),
                ('company_name', models.CharField(max_length=255, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('address1', models.CharField(max_length=255, verbose_name=b'Street Address')),
                ('address2', models.CharField(max_length=255, verbose_name=b'Apt/Suite/Bldg', blank=True)),
                ('city', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=200, verbose_name=b'State/Province')),
                ('postal_code', models.CharField(max_length=20, verbose_name=b'ZIP/Postal Code')),
                ('country', models.CharField(max_length=200)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='Car',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('make', models.CharField(max_length=100)),
                ('model', models.CharField(max_length=100)),
                ('year', models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(2050), django.core.validators.MinValueValidator(1887)])),
                ('color', models.CharField(max_length=50)),
                ('plate', models.CharField(max_length=15)),
                ('mileage', models.PositiveIntegerField(null=True, blank=True)),
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
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('stripe_customer_id', models.CharField(max_length=50, blank=True)),
                ('type', models.CharField(default=b'customer', max_length=15, choices=[(b'customer', b'customer'), (b'technician', b'technician')])),
                ('points', models.PositiveIntegerField(default=0)),
                ('phone_number', models.CharField(max_length=20, blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
