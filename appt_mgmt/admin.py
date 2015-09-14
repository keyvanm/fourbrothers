from django.contrib import admin

from models import ServicedCar, Service, Appointment

admin.site.register(Service)
admin.site.register(Appointment)
admin.site.register(ServicedCar)
