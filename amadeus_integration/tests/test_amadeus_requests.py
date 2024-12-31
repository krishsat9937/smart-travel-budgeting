from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class GetAmadeusTokenTestCase(TestCase):
    @patch("amadeus_integration.views.get_amadeus_token")
    def test_get_amadeus_token_success(self, mock_get_token):
        # Mocking the response for get_amadeus_token
        mock_get_token.return_value = "test-token"  # Expected mock token

        response = self.client.post(reverse("get-amadeus-token"))

        # Assert that the response is correct
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"token": "test-token"})


    @patch("amadeus_integration.views.get_amadeus_token")
    def test_get_amadeus_token_failure(self, mock_get_token):
        # Simulate failure in getting token
        mock_get_token.return_value = None  # This should trigger a 500 error in the view

        response = self.client.post(reverse("get-amadeus-token"))

        # Assert that a 500 response is returned
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"error": "Failed to get Amadeus token"})
