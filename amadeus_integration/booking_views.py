import json
import traceback
from logging import getLogger
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from amadeus_integration.models import Booking
from amadeus_integration.serializers import BookingSerializer
from amadeus_integration.util import get_amadeus_token
import requests
from rest_framework.permissions import IsAuthenticated
from amadeus_integration.util import store_booking
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist



logger = getLogger(__name__)

class BookFlightsRequest(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract and decode the flightOffer field
            flight_offer_raw = request.data.get("flightOffer")
            if not flight_offer_raw:
                return Response(
                    {"error": "Missing flightOffer field"}, status=status.HTTP_400_BAD_REQUEST
                )

            try:
                flight_offer = json.loads(flight_offer_raw)
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding flightOffer: {e}")
                return Response(
                    {"error": "Invalid flightOffer JSON format"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Extract passengers, email, and address
            passengers = request.data.get("passengers")
            email = request.data.get("email")
            address = request.data.get("address")  # Expecting address field from frontend

            if not passengers or not email or not address:
                return Response(
                    {"error": "Missing passengers, email, or address fields"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get Amadeus token
            token = get_amadeus_token()
            if not token:
                logger.error("Failed to fetch Amadeus token.")
                return Response(
                    {"error": "Failed to get Amadeus token"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Prepare the booking payload
            booking_payload = {
                "data": {
                    "type": "flight-order",  # Mandatory field
                    "flightOffers": [flight_offer],
                    "travelers": [
                        {
                            "id": str(index + 1),
                            "dateOfBirth": passenger["dateOfBirth"],
                            "name": {
                                "firstName": passenger["firstName"],
                                "lastName": passenger["lastName"],
                            },
                            "documents": [
                                {
                                    "documentType": "PASSPORT",
                                    "number": passenger["passportNumber"],
                                    "expiryDate": passenger.get("passportExpiryDate"),  # Expect expiryDate from frontend
                                    "holder": True,  # Default value for holder
                                    "issuanceCountry": passenger.get("issuanceCountry", "US"),
                                    "nationality": passenger.get("nationality", "US"),
                                }
                            ],
                        }
                        for index, passenger in enumerate(passengers)
                    ],
                    "contacts": [
                        {
                            "addresseeName": {
                                "firstName": passengers[0]["firstName"],
                                "lastName": passengers[0]["lastName"],
                            },
                            "emailAddress": email,
                            "purpose": "STANDARD",  # Mandatory field
                            "address": {
                                "lines": address["lines"],
                                "postalCode": address["postalCode"],
                                "cityName": address["city"],
                                "countryCode": address["countryCode"],
                            },
                        }
                    ],
                }
            }

            # Call the Amadeus booking API
            booking_url = "https://test.api.amadeus.com/v1/booking/flight-orders"
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.amadeus+json",
                "Content-Type": "application/json",
            }

            logger.info(f"Sending booking payload: {json.dumps(booking_payload, indent=2)}")
            response = requests.post(booking_url, json=booking_payload, headers=headers)

            # Handle the API response
            if response.status_code == 201:
                booking_data = response.json()  
                # Store the booking in the database
                try:
                    with transaction.atomic():
                        booking = store_booking(request.user, booking_data)
                        # Serialize and return the stored booking
                        serialized_booking = BookingSerializer(booking)
                        logger.info(f"Booking stored successfully: {booking}")
                except ValueError as e:
                    logger.error(f"Error storing booking: {e}")
                    return Response(
                        {"error": "Failed to store booking", "details": str(e)},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

                return Response(
                    {"message": "Booking successful", "data": serialized_booking.data},
                    status=status.HTTP_201_CREATED,
                )                
            else:
                logger.error(f"Booking failed: {response.status_code}, {response.text}")
                return Response(
                    {"error": "Booking failed", "details": response.json()},
                    status=response.status_code,
                )

        except Exception as e:
            logger.error(traceback.format_exc())
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class BookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Fetch bookings for the authenticated user
            user = request.user
            bookings = Booking.objects.filter(user=user).order_by('-creation_date')  # Latest first

            # Serialize the bookings
            serializer = BookingSerializer(bookings, many=True)

            # Return serialized bookings
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response({"error": "No bookings found for the user"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
