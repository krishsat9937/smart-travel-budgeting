from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

class BestTravelOptionsTestCase(TestCase):
    @patch("amadeus_integration.views.get_amadeus_token")
    @patch("amadeus_integration.views.recommend_best_options")
    def test_get_best_travel_options_success(self, mock_recommend, mock_get_token):
        # Mocking responses
        mock_get_token.return_value = "test-token"
        mock_recommend.return_value = {"recommendations": [{"id": "1", "price": 150}]}
        
        # Query parameters
        params = {
            "originLocationCode": "NYC",
            "destinationLocationCode": "LAX",
            "departureDate": "2024-12-31",
            "returnDate": "2025-01-07",
            "adults": 2,
            "radius": 100,
        }
        
        response = self.client.get(reverse("best-travel-options"), params)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"recommendations": [{"id": "1", "price": 150}]})

    @patch("amadeus_integration.views.get_amadeus_token")
    def test_get_best_travel_options_token_failure(self, mock_get_token):
        # Simulate token failure
        mock_get_token.return_value = None
        
        response = self.client.get(reverse("best-travel-options"), {
            "originLocationCode": "NYC",
            "destinationLocationCode": "LAX",
            "departureDate": "2024-12-31",
            "returnDate": "2025-01-07",
            "adults": 2,
        })
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"error": "Failed to get Amadeus token"})