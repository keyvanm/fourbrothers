from django.contrib import admin

from models import *

admin.site.register(UserProfile)

admin.site.register(Address)
admin.site.register(PrivateParkingLocation)
admin.site.register(SharedParkingLocation)
admin.site.register(Building)
admin.site.register(BuildingPreScheduledTimeSlot)

admin.site.register(Car)
admin.site.register(CreditCard)
admin.site.register(PromoCode)
