import traceback

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from logging import getLogger

from amadeus_integration.util import (
    get_amadeus_token,
    get_flight_offers,
    get_iata_code,
    recommend_best_options,
)
from amadeus_integration.parsers import FlightOfferParser
from rest_framework import serializers


logger = getLogger(__name__)


class BooleanField(serializers.Field):
    def to_internal_value(self, data):
        if type(data) is bool:
            return data
        elif type(data) is str:
            return data.lower() == "true"
        return False

    def to_representation(self, value):
        return "true" if value else "false"


class FlightOffersRequestSerializer(serializers.Serializer):
    originLocationCode = serializers.CharField(required=True)
    destinationLocationCode = serializers.CharField(required=True)
    departureDate = serializers.DateField(required=True)
    returnDate = serializers.DateField(required=True)
    adults = serializers.IntegerField(required=True)
    nonStop = BooleanField(required=False)
    max = serializers.IntegerField(required=False)


class GetAmadeusToken(APIView):
    def post(self, request, *args, **kwargs):
        try:
            token = get_amadeus_token()
            return_data = {"token": token}
            if not token:
                return Response(
                    {"error": "Failed to get Amadeus token"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return Response(return_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GetFlightOffers(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="originLocationCode",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="destinationLocationCode",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="departureDate",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="returnDate",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="adults",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="nonStop",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
            openapi.Parameter(
                name="max",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        params = {
            "originLocationCode": request.query_params.get("originLocationCode"),
            "destinationLocationCode": request.query_params.get(
                "destinationLocationCode"
            ),
            "departureDate": request.query_params.get("departureDate"),
            "returnDate": request.query_params.get("returnDate"),
            "adults": request.query_params.get("adults"),
            "nonStop": request.query_params.get("nonStop"),
            "max": request.query_params.get("max", 100),
        }

        # get amedeus token using the client credentials flow
        token = get_amadeus_token()
        print(f"Amadeus token response: {token}")

        if not token:
            return Response(
                {"error": "Failed to get Amadeus token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        bearer_token = f"Bearer {token}"
        print(f"Bearer token: {bearer_token}")

        # get IATA codes for the origin and destination locations
        origin_code = get_iata_code(params["originLocationCode"], token)
        destination_code = get_iata_code(params["destinationLocationCode"], token)

        if not origin_code or not destination_code:
            return Response(
                {"error": "Failed to get IATA codes for locations"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        params["originLocationCode"] = origin_code
        params["destinationLocationCode"] = destination_code

        response = get_flight_offers(bearer_token, params)
        
        return Response(response, status=status.HTTP_200_OK)
                
        

    @swagger_auto_schema(
        operation_description="Get flight offers",
        request_body=FlightOffersRequestSerializer,
        responses={
            200: "Flight offers data",
            400: "Bad request",
            401: "Unauthorized",
            500: "Internal server error",
        },
    )
    @method_decorator(cache_page(60 * 10))
    def post(self, request, *args, **kwargs):
        try:
            params = {
                "originLocationCode": request.data.get("originLocationCode"),
                "destinationLocationCode": request.data.get("destinationLocationCode"),
                "departureDate": request.data.get("departureDate"),
                "returnDate": request.data.get("returnDate"),
                "adults": request.data.get("adults"),
                "nonStop": request.data.get("nonStop"),
                "max": request.data.get("max", 100),
            }

            # get amedeus token using the client credentials flow
            token = get_amadeus_token()
            print(f"Amadeus token response: {token}")

            if not token:
                return Response(
                    {"error": "Failed to get Amadeus token"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            bearer_token = f"Bearer {token}"
            print(f"Bearer token: {bearer_token}")

            # get IATA codes for the origin and destination locations
            origin_code = get_iata_code(params["originLocationCode"], token)
            destination_code = get_iata_code(params["destinationLocationCode"], token)

            if not origin_code or not destination_code:
                return Response(
                    {"error": "Failed to get IATA codes for locations"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            params["originLocationCode"] = origin_code
            params["destinationLocationCode"] = destination_code

            for key, value in params.items():
                if isinstance(value, bool):
                    params[key] = "true" if value else "false"

            response = get_flight_offers(bearer_token, params)
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BestTravelOptions(APIView):
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name="originLocationCode",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="destinationLocationCode",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                name="departureDate",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="returnDate",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                format=openapi.FORMAT_DATE,
                required=True,
            ),
            openapi.Parameter(
                name="adults",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=True,
            ),
            openapi.Parameter(
                name="nonStop",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_BOOLEAN,
                required=False,
            ),
            openapi.Parameter(
                name="max",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                name="radius",
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        # Extract query parameters
        params = {
            "originLocationCode": request.query_params.get("originLocationCode"),
            "destinationLocationCode": request.query_params.get(
                "destinationLocationCode"
            ),
            "departureDate": request.query_params.get("departureDate"),
            "returnDate": request.query_params.get("returnDate"),
            "adults": request.query_params.get("adults"),
            "nonStop": request.query_params.get("nonStop"),
            "max": request.query_params.get("max", 100),
            "radius": request.query_params.get("radius", 50),
        }

        # get amedeus token using the client credentials flow
        token = get_amadeus_token()
        print(f"Amadeus token response: {token}")

        if not token:
            return Response(
                {"error": "Failed to get Amadeus token"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        recommendations = recommend_best_options(
            token,
            params,
            params["originLocationCode"],
            params["destinationLocationCode"],
            radius=params["radius"],
        )
        return Response(recommendations)
    
    @swagger_auto_schema(
        operation_description="Get best travel options",
        request_body=FlightOffersRequestSerializer,
        responses={
            200: "Best travel options data",
            400: "Bad request",
            401: "Unauthorized",
            500: "Internal server error",
        },
    )
    def post(self, request, *args, **kwargs):
        try:
            # Extract parameters from the request body
            params = {
                "originLocationCode": request.data.get("originLocationCode"),
                "destinationLocationCode": request.data.get("destinationLocationCode"),
                "departureDate": request.data.get("departureDate"),
                "returnDate": request.data.get("returnDate"),
                "adults": request.data.get("adults"),
                "nonStop": request.data.get("nonStop", False),
                "max": request.data.get("max", 100),
                "radius": request.data.get("radius", 50),
            }

            # Validate required fields
            missing_fields = [
                field
                for field in ["originLocationCode", "destinationLocationCode", "departureDate", "returnDate", "adults"]
                if not params.get(field)
            ]
            if missing_fields:
                return Response(
                    {"error": f"Missing required fields: {', '.join(missing_fields)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get Amadeus token
            token = get_amadeus_token()
            print(f"Amadeus token response: {token}")

            if not token:
                return Response(
                    {"error": "Failed to get Amadeus token"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Call recommendation logic with the token
            recommendations = recommend_best_options(
                token,
                params,
                params["originLocationCode"],
                params["destinationLocationCode"],
                radius=params["radius"],
            )

            return Response(recommendations, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in BestTravelOptions POST: {str(e)}")
            traceback.print_exc()            
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
