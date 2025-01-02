from datetime import datetime
from unittest.mock import patch, MagicMock
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from amadeus_integration.models import (
    Booking,
    Traveler,
    Contact,
    FlightSegment,
    Itinerary,
    Price,
)

class ApiUrlsTestCase(TestCase):
    def setUp(self):
        # Initialize API client and authenticate user
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="testpassword")
        self.client.force_authenticate(user=self.user)

        # Create mock data for testing
        self.traveler = Traveler.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth="1990-01-01",
            passport_number="123456789",
            passport_expiry_date="2030-01-01",
            passport_issuance_country="US",
            nationality="US",
        )

        self.contact = Contact.objects.create(
            email="test@example.com",
            addressee_name="John Doe",
            address_lines="123 Test St",
            postal_code="12345",
            city_name="Test City",
            country_code="US",
        )

        self.price = Price.objects.create(
            currency="USD",
            total=500.0,
            base=400.0,
            refundable_taxes=50.0,
            grand_total=550.0,
        )

        self.flight_segment = FlightSegment.objects.create(
            departure_iata_code="JFK",
            departure_terminal="1",
            departure_time="2025-01-10T10:00:00Z",
            arrival_iata_code="LAX",
            arrival_terminal="2",
            arrival_time="2025-01-10T14:00:00Z",
            carrier_code="AA",
            flight_number="100",
            aircraft_code="777",
            duration="4h",
            number_of_stops=0,
            co2_emissions_weight=100.0,
            co2_emissions_unit="kg",
            cabin="economy",
        )

        self.itinerary = Itinerary.objects.create()
        self.itinerary.segments.add(self.flight_segment)

        self.booking = Booking.objects.create(
            user=self.user,
            booking_id="eJzTd9f3dvSw9AwCAArnAk4%3D",
            reference="KAH9IR",
            creation_date=datetime.now(),
            flight_offer_id="123456",
            price=self.price,
            ticketing_option="CONFIRM",
        )
        self.booking.travelers.add(self.traveler)
        self.booking.contacts.add(self.contact)
        self.booking.itineraries.add(self.itinerary)

    def test_get_bookings(self):
        response = self.client.get("/bookings/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["reference"], "KAH9IR")

    @patch("amadeus_integration.booking_views.get_amadeus_token")
    @patch("requests.post")
    @patch("amadeus_integration.booking_views.store_booking")
    def test_book_flight(self, mock_store_booking, mock_requests_post, mock_get_amadeus_token):
        mock_get_amadeus_token.return_value = "test-token"
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"booking": "data"}
        mock_requests_post.return_value = mock_response
        mock_store_booking.return_value = self.booking

        valid_payload = {
            "flightOffer": '{"key": "value"}',
            "passengers": [
                {
                    "firstName": "John",
                    "lastName": "Doe",
                    "dateOfBirth": "1990-01-01",
                    "passportNumber": "123456789",
                    "passportExpiryDate": "2030-01-01",
                    "issuanceCountry": "US",
                    "nationality": "US",
                }
            ],
            "email": "test@example.com",
            "address": {
                "lines": ["123 Test St"],
                "postalCode": "12345",
                "city": "Test City",
                "countryCode": "US",
            },
        }

        response = self.client.post("/book-flight/", valid_payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("message", response.data)
        self.assertEqual(response.data["message"], "Booking successful")