from rest_framework import serializers
from amadeus_integration.models import (
    Booking,
    Traveler,
    Contact,
    FlightSegment,
    Itinerary,
    Price,
    Warning,
)

class TravelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveler
        fields = [
            'first_name',
            'last_name',
            'date_of_birth',
            'passport_number',
            'passport_expiry_date',
            'passport_issuance_country',
            'nationality',
        ]

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = [
            'email',
            'addressee_name',
            'address_lines',
            'postal_code',
            'city_name',
            'country_code',
        ]

class FlightSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightSegment
        fields = [
            'departure_iata_code',
            'departure_terminal',
            'departure_time',
            'arrival_iata_code',
            'arrival_terminal',
            'arrival_time',
            'carrier_code',
            'flight_number',
            'aircraft_code',
            'duration',
            'number_of_stops',
            'co2_emissions_weight',
            'co2_emissions_unit',
            'cabin',
        ]

class ItinerarySerializer(serializers.ModelSerializer):
    segments = FlightSegmentSerializer(many=True)

    class Meta:
        model = Itinerary
        fields = ['segments']

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['currency', 'total', 'base', 'refundable_taxes', 'grand_total']

class WarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warning
        fields = ['title', 'detail']

class BookingSerializer(serializers.ModelSerializer):
    travelers = TravelerSerializer(many=True)
    contacts = ContactSerializer(many=True)
    itineraries = ItinerarySerializer(many=True)
    price = PriceSerializer()
    warnings = WarningSerializer(many=True)

    class Meta:
        model = Booking
        fields = [
            'id',
            'user',
            'booking_id',
            'reference',
            'creation_date',
            'flight_offer_id',
            'travelers',
            'contacts',
            'itineraries',
            'price',
            'ticketing_option',
            'warnings',
        ]
