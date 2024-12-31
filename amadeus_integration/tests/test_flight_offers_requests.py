from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

class GetFlightOffersTestCase(TestCase):
    @patch("amadeus_integration.views.get_amadeus_token")
    @patch("amadeus_integration.views.get_iata_code")
    @patch("amadeus_integration.views.get_flight_offers")
    def test_get_flight_offers_success(self, mock_get_flight_offers, mock_get_iata_code, mock_get_token):
        # Mocking responses
        mock_get_token.return_value = "test-token"
        mock_get_iata_code.side_effect = ["IATA1", "IATA2"]  # Origin and destination codes
        mock_get_flight_offers.return_value = {"flights": [{"id": "1", "price": 100}]}
        
        # Query parameters
        params = {
            "originLocationCode": "NYC",
            "destinationLocationCode": "LAX",
            "departureDate": "2024-12-31",
            "returnDate": "2025-01-07",
            "adults": 2,
            "nonStop": True,
            "max": 5,
        }
        
        response = self.client.get(reverse("get-flight-offers"), params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"flights": [{"id": "1", "price": 100}]})

    @patch("amadeus_integration.views.get_amadeus_token")
    def test_get_flight_offers_token_failure(self, mock_get_token):
        # Simulate token failure
        mock_get_token.return_value = None
        
        response = self.client.get(reverse("get-flight-offers"), {
            "originLocationCode": "NYC",
            "destinationLocationCode": "LAX",
            "departureDate": "2024-12-31",
            "returnDate": "2025-01-07",
            "adults": 2,
        })
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"error": "Failed to get Amadeus token"})