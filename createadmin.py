#!/usr/bin/env python

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fourbrothers.settings")
import django

django.setup()

from django.contrib.auth.models import User, Group

if User.objects.count() == 0:
    fourbros_staff = Group(name="Fourbrothers Staff")
    fourbros_staff.save()

    keyvan = User.objects.create_user('keyvan', 'kayvanmsh@gmail.com', 'password')
    keyvan.first_name = "Keyvan"
    keyvan.last_name = "Mosharraf"
    keyvan.is_superuser = True
    keyvan.is_staff = True
    keyvan.save()
    keyvan.groups.add(fourbros_staff)

    jeff = User.objects.create_user('jeff', 'jeff@superawesome.ca', 'password')
    jeff.first_name = "Jeff"
    jeff.last_name = "Gingras"
    jeff.is_staff = True
    jeff.save()
    jeff.groups.add(fourbros_staff)

    adam = User.objects.create_user('adam', 'adam@fourbrothers.ca', 'password')
    adam.first_name = "Adam"
    adam.last_name = "Zameret"
    adam.is_staff = True
    adam.save()
    adam.groups.add(fourbros_staff)

    technician = User.objects.create_user('techi', 't@hc.com', 'password')
    technician.first_name = 'Techi'
    technician.last_name = 'Nician'
    technician.save()
    technician.profile.type = 'technician'
    technician.profile.save()
