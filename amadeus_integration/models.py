from django.db import models
from django.contrib.auth.models import User


class Traveler(models.Model):
    objects = models.Manager()

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    passport_number = models.CharField(max_length=50)
    passport_expiry_date = models.DateField()
    passport_issuance_country = models.CharField(max_length=10)
    nationality = models.CharField(max_length=10)

class Contact(models.Model):
    objects = models.Manager()

    email = models.EmailField()
    addressee_name = models.CharField(max_length=200)
    address_lines = models.TextField()  # To handle multiple lines
    postal_code = models.CharField(max_length=20)
    city_name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)

class FlightSegment(models.Model):
    objects = models.Manager()

    departure_iata_code = models.CharField(max_length=10)
    departure_terminal = models.CharField(max_length=50, blank=True, null=True)
    departure_time = models.DateTimeField()
    arrival_iata_code = models.CharField(max_length=10)
    arrival_terminal = models.CharField(max_length=50, blank=True, null=True)
    arrival_time = models.DateTimeField()
    carrier_code = models.CharField(max_length=10)
    flight_number = models.CharField(max_length=20)
    aircraft_code = models.CharField(max_length=10)
    duration = models.CharField(max_length=50)
    number_of_stops = models.IntegerField()
    co2_emissions_weight = models.FloatField()
    co2_emissions_unit = models.CharField(max_length=10)
    cabin = models.CharField(max_length=20)

class Itinerary(models.Model):
    objects = models.Manager()

    segments = models.ManyToManyField(FlightSegment)

class Price(models.Model):
    objects = models.Manager()

    currency = models.CharField(max_length=10)
    total = models.FloatField()
    base = models.FloatField()
    refundable_taxes = models.FloatField()
    grand_total = models.FloatField()

class Booking(models.Model):
    objects = models.Manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    booking_id = models.CharField(max_length=50, unique=True)  # eJzTd9f3dvSw9AwCAArnAk4%3D
    reference = models.CharField(max_length=20)  # KAH9IR
    creation_date = models.DateTimeField()
    flight_offer_id = models.CharField(max_length=20)
    travelers = models.ManyToManyField('Traveler')
    contacts = models.ManyToManyField('Contact')
    itineraries = models.ManyToManyField('Itinerary')
    price = models.OneToOneField('Price', on_delete=models.CASCADE)
    ticketing_option = models.CharField(max_length=20)  # CONFIRM

class Warning(models.Model):
    objects = models.Manager()
    
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="warnings")
    title = models.CharField(max_length=200)
    detail = models.TextField()
