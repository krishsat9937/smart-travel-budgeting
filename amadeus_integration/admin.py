from django.contrib import admin
from .models import Booking, Traveler, Contact, FlightSegment, Itinerary, Price, Warning

# Register your models here
admin.site.register(Booking)
admin.site.register(Traveler)
admin.site.register(Contact)
admin.site.register(FlightSegment)
admin.site.register(Itinerary)
admin.site.register(Price)
admin.site.register(Warning)
