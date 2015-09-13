# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import django_extensions.db.fields


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
                ('primary', models.BooleanField(default=False)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('phone_number', models.CharField(max_length=200, blank=True)),
                ('company_name', models.CharField(max_length=255, blank=True)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('address1', models.CharField(max_length=255, verbose_name=b'Street Address')),
                ('address2', models.CharField(max_length=255, verbose_name=b'Apt/Suite/Bldg', blank=True)),
                ('city', models.CharField(max_length=200)),
                ('state', models.CharField(max_length=200, verbose_name=b'State/Province')),
                ('postal_code', models.CharField(max_length=20, verbose_name=b'ZIP/Postal Code')),
                ('country', models.CharField(max_length=200)),
                ('user', models.ForeignKey(related_name='personal_addresses', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name_plural': 'addresses',
            },
        ),
        migrations.CreateModel(
            name='CreditCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('card_id', models.CharField(max_length=50)),
                ('fingerprint', models.CharField(max_length=50)),
                ('user', models.ForeignKey(related_name='creditcards', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=20, blank=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
