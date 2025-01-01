import json
import re
import os
import hashlib


import googlemaps
import requests

from datetime import datetime, timedelta
from django.core.cache import cache

from amadeus_integration.parsers import FlightOfferParser
from .constants import CITIES
from datetime import datetime
from .models import Booking, Traveler, Contact, FlightSegment, Itinerary, Price, Warning
from django.db import transaction
# from django.utils.timezone import now
from amadeus_integration.models import (
    Booking,
    Traveler,
    Contact,
    FlightSegment,
    Itinerary,
    Price,
    Warning,
)




googlemaps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Define a global variable to store the cached token and its expiry time
cached_token = None
expiry_time = None


def get_amadeus_token():
    global cached_token
    global expiry_time

    # Check if the token is already cached and has not expired
    if cached_token and expiry_time and expiry_time > datetime.now():
        return cached_token

    url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }

    # get client credentials from environment variables
    client_id = os.getenv("AMADEUS_CLIENT_ID")
    client_secret = os.getenv("AMADEUS_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise ValueError(
            "AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET must be set in the environment variables"
        )

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(url, headers=headers, data=data)

    # Cache the token and its expiry time
    if response.status_code == 200:
        token_data = response.json()
        cached_token = token_data["access_token"]
        expiry_seconds = token_data["expires_in"]
        expiry_time = datetime.now() + timedelta(seconds=expiry_seconds)

    return cached_token


def get_iata_code(city_name, api_key):
    """
    Get the IATA code for a given city name using the Amadeus API.

    Parameters:
    - city_name: The name of the city to lookup.
    - api_key: Your Amadeus API key.

    Returns:
    - The IATA code as a string if found, otherwise None.
    """

    # Endpoint for the Amadeus location search API
    url = f"https://test.api.amadeus.com/v1/reference-data/locations?subType=CITY&keyword={city_name}"

    # Headers to include your API key for authentication
    headers = {"Authorization": f"Bearer {api_key}"}

    cached_response = cache.get(city_name)

    try:

        if cached_response:
            print(f"Using cached response for {city_name}")
            data = cached_response
        else:
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors

            # Cache the response for future use
            cache.set(city_name, response.json(), timeout=300)  # Cache for 1 hour

            # Parse the JSON response
            data = response.json()

        # Check if we have any results
        if data and "data" in data and len(data["data"]) > 0:
            # Return the first IATA code found
            return data["data"][0]["iataCode"]
        else:
            return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def parse_duration(duration_str):
    """Convert a duration string (e.g., '9h 45m') into total minutes."""
    hours, minutes = 0, 0
    if "h" in duration_str:
        parts = duration_str.split("h")
        hours = int(parts[0])
        if "m" in parts[1]:
            minutes = int(parts[1].replace("m", "").strip())
    elif "m" in duration_str:
        minutes = int(duration_str.replace("m", "").strip())
    return hours * 60 + minutes


def get_top_3_offers(flight_offers):
    """
    Get the top 3 raw flight offers based on cost and duration without parsing.

    Parameters:
    - flight_offers (list): List of flight offers in JSON format.

    Returns:
    - list: Top 3 raw flight offers ranked by cost and duration.
    """

    def get_total_duration(itineraries):
        """
        Calculate the total duration of all itineraries.
        """
        total_duration = 0
        for itinerary in itineraries:
            total_duration += parse_duration(itinerary["duration"])
        return total_duration

    # Add sorting keys to each offer
    for offer in flight_offers:
        offer["total_duration"] = get_total_duration(offer["itineraries"])
        offer["price_float"] = float(offer["price"])

    # Sort the raw offers by price and total duration
    sorted_offers = sorted(
        flight_offers, key=lambda x: (x["price_float"], x["total_duration"], x["id"])
    )

    # Return the top 3 offers
    return sorted_offers[:3]


def get_flight_offers(bearer_token, params):
    try:
        cache.clear()
        flight_offers = []
        # Generate a stable and unique cache key using a hash of the parameters
        params_string = json.dumps(
            params, sort_keys=True
        )  # Convert params to a sorted JSON string
        cache_key = (
            f"flight_offers_{hashlib.sha256(params_string.encode()).hexdigest()}"
        )

        # Check the cache for existing results
        cached_response = cache.get(cache_key)
        if cached_response:
            print(f"Using cached flight offers for params: {params}")
            return cached_response

        # Otherwise, make the API request
        url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        headers = {
            "Authorization": bearer_token,
            "accept": "application/vnd.amadeus+json",
            "connection": "keep-alive",
        }

        print(f"Params: {params}")
        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code == 200:
            parser = FlightOfferParser(response.json())
            flight_offers = parser.parse_offers()

            # print(f"Flight offers: {json.dumps(flight_offers)}")

            # Cache the parsed flight offers for a defined timeout (e.g., 1 hour)
            cache.set(cache_key, flight_offers, timeout=300)
            print(f"Cached flight offers for params: {params}")
        else:
            print(
                f"Failed to fetch flight offers: {response.status_code} - {response.text}"
            )
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

    return flight_offers


def get_city_and_country_from_iata_code(iata_code):
    for city in CITIES:
        if city["code"] == iata_code:
            return city["city"], city["country"]
    return None, None


def check_if_international_trip(origin_code, destination_code):
    def get_country_by_code(code):
        for city in CITIES:
            if city["code"] == code:
                return city["country"]
        return None

    origin_country = get_country_by_code(origin_code)
    destination_country = get_country_by_code(destination_code)

    if not origin_country or not destination_country:
        return f"Invalid airport code(s): {origin_code}, {destination_code}"

    return origin_country != destination_country


def get_airport_codes_in_country(origin_code):
    return [
        city["code"]
        for city in CITIES
        if city["country"]
        == next((c["country"] for c in CITIES if c["code"] == origin_code), None)
        and city["code"] != origin_code
    ]

def extract_transit_details(directions_result):
    transit_details_list = []
    
    for route in directions_result:
        for leg in route.get("legs", []):
            for step in leg.get("steps", []):
                transit_details = step.get("transit_details")
                if transit_details:
                    transit_info = {
                        "departure_stop": transit_details.get("departure_stop", {}).get("name"),
                        "arrival_stop": transit_details.get("arrival_stop", {}).get("name"),
                        "departure_time": datetime.utcfromtimestamp(transit_details.get("departure_time", {}).get("value")).isoformat() if transit_details.get("departure_time") else None,
                        "arrival_time": datetime.utcfromtimestamp(transit_details.get("arrival_time", {}).get("value")).isoformat() if transit_details.get("arrival_time") else None,
                        "num_stops": transit_details.get("num_stops"),
                        "vehicle": transit_details.get("line", {}).get("vehicle", {}).get("name"),
                        "line_name": transit_details.get("line", {}).get("name"),
                        "agency_name": transit_details.get("line", {}).get("agencies", [{}])[0].get("name"),
                        "agency_url": transit_details.get("line", {}).get("agencies", [{}])[0].get("url"),
                    }
                    transit_details_list.append(transit_info)
    
    return transit_details_list


def add_transit_options_to_international_flight_itineraries(
    flight_offers, origin_location_city, destination_location_city
):
    print(
        f"Adding transit options to flight itineraries for {origin_location_city} to {destination_location_city}"
    )
    # Placeholder for fetching alternative transportation options from an airport to the final destination    
    gmaps = googlemaps.Client(key=googlemaps_api_key)

    for offer in flight_offers:
        journey_start_itinerary = offer["itineraries"][0]
        journey_end_itinerary = offer["itineraries"][-1]

        arrival_airport_code = journey_start_itinerary["segments"][-1]["arrival"]
        arrival_airport_time = datetime.strptime(journey_start_itinerary["segments"][-1]["arrivalTime"], "%Y-%m-%dT%H:%M:%S")

        print(f"Arrival airport code: {arrival_airport_code} at {arrival_airport_time}")

        arrival_airport_city, arrival_city_country = (
            get_city_and_country_from_iata_code(arrival_airport_code)
        )

        print(f"Arrival airport city: {arrival_airport_city}, country: {arrival_city_country}")

        if not arrival_airport_city or not arrival_city_country:
            print(f"Invalid arrival airport code: {arrival_airport_code}")
            continue

        if arrival_airport_city == destination_location_city:
            print(f"Skipping domestic flight to {arrival_city_country}")
            continue

        # Fetch directions for the current mode of transport
        directions_result = gmaps.directions(
            origin=f"{arrival_airport_city} airport",
            destination=destination_location_city,
            mode="transit",
            departure_time=arrival_airport_time,
            transit_mode=["bus"],  # Specify transit mode
            transit_routing_preference="fewer_transfers",  # Routing preference
            units="imperial",  # Unit system
        )

        if directions_result:
            transit_details = extract_transit_details(directions_result)
            print(f"Transit details: {json.dumps(transit_details)}")
            journey_start_itinerary["transit_details"] = transit_details


        departure_airport_code = journey_end_itinerary["segments"][0]["departure"]
        departure_airport_time = datetime.strptime(journey_end_itinerary["segments"][0]["departureTime"], "%Y-%m-%dT%H:%M:%S")

        print(f"Departure airport code: {departure_airport_code} at {departure_airport_time}")

        departure_airport_city, departure_city_country = (
            get_city_and_country_from_iata_code(departure_airport_code)
        )

        print(f"Departure airport city: {departure_airport_city}, country: {departure_city_country}")

        if not departure_airport_city or not departure_city_country:
            print(f"Invalid departure airport code: {departure_airport_code}")
            continue

        if departure_airport_city == origin_location_city:
            print(f"Skipping domestic flight from {departure_city_country}")
            continue

        # Fetch directions for the current mode of transport
        directions_result = gmaps.directions(
            origin=destination_location_city,
            destination=f"{departure_airport_city} airport",
            mode="transit",
            arrival_time=departure_airport_time,
            transit_mode=["bus"],  # Specify transit mode
            transit_routing_preference="fewer_transfers",  # Routing preference
            units="imperial",  # Unit system
        )

        if directions_result:
            transit_details = extract_transit_details(directions_result)
            print(f"Transit details: {json.dumps(transit_details)}")
            journey_end_itinerary["transit_details"] = transit_details

    return flight_offers        

def add_transit_options_to_domestic_flight_itineraries(
    flight_offers, origin_location_city, destination_location_city
):
    print(
        f"Adding transit options to domestic flight itineraries for {origin_location_city} to {destination_location_city}"
    )
    # Placeholder for fetching alternative transportation options from an airport to the final destination    
    gmaps = googlemaps.Client(key=googlemaps_api_key)

    for offer in flight_offers:
        journey_start_itinerary = offer["itineraries"][0]
        journey_end_itinerary = offer["itineraries"][-1]

        departure_airport_code = journey_start_itinerary["segments"][0]["departure"]
        departure_airport_time = datetime.strptime(journey_start_itinerary["segments"][0]["departureTime"], "%Y-%m-%dT%H:%M:%S")

        print(f"Departure airport code: {departure_airport_code} at {departure_airport_time}")

        departure_airport_city, departure_city_country = (
            get_city_and_country_from_iata_code(departure_airport_code)
        )

        print(f"Departure airport city: {departure_airport_city}, country: {departure_city_country}")

        if not departure_airport_city or not departure_city_country:
            print(f"Invalid arrival airport code: {departure_airport_code}")
            continue

        # Fetch directions for the current mode of transport
        directions_result = gmaps.directions(
            origin=origin_location_city,
            destination=f"{departure_airport_city} airport",
            mode="transit",
            arrival_time=departure_airport_time,
            transit_mode=["bus"],  # Specify transit mode
            transit_routing_preference="fewer_transfers",  # Routing preference
            units="imperial",  # Unit system
        )

        if directions_result:
            transit_details = extract_transit_details(directions_result)
            print(f"Transit details: {json.dumps(transit_details)}")
            journey_start_itinerary["transit_details"] = transit_details


        arrival_airport_code = journey_end_itinerary["segments"][0]["arrival"]
        arrival_airport_time = datetime.strptime(journey_end_itinerary["segments"][0]["arrivalTime"], "%Y-%m-%dT%H:%M:%S")

        print(f"Arrival airport code: {arrival_airport_code} at {arrival_airport_time}")

        arrival_airport_city, arrival_city_country = (
            get_city_and_country_from_iata_code(arrival_airport_code)
        )

        print(f"Arrival airport city: {arrival_airport_city}, country: {arrival_city_country}")

        if not arrival_airport_city or not arrival_city_country:
            print(f"Invalid arrival airport code: {arrival_airport_code}")
            continue
        
        # Fetch directions for the current mode of transport
        directions_result = gmaps.directions(
            origin=f"{arrival_airport_city} airport",
            destination=origin_location_city,
            mode="transit",
            departure_time=arrival_airport_time,
            transit_mode=["bus"],  # Specify transit mode
            transit_routing_preference="fewer_transfers",  # Routing preference
            units="imperial",  # Unit system
        )

        if directions_result:
            transit_details = extract_transit_details(directions_result)
            print(f"Transit details: {json.dumps(transit_details)}")
            journey_end_itinerary["transit_details"] = transit_details

    return flight_offers        

def recommend_best_options(
    token, params, origin_location_city, destination_location_city, radius=10
):
    all_flight_offers = []

    print(
        f"Recommending best options for {origin_location_city} to {destination_location_city}"
    )
    params["originLocationCode"] = get_iata_code(origin_location_city, token)
    params["destinationLocationCode"] = get_iata_code(destination_location_city, token)

    bearer_token = f"Bearer {token}"

    params_without_radius = params.copy()
    params_without_radius.pop("radius")

    params_without_radius["nonStop"] = "false"

    # Get flight offers from Amadeus API
    initial_flight_offer = get_flight_offers(bearer_token, params_without_radius)

    all_flight_offers.extend(initial_flight_offer)

    def get_flight_offers_for_airports(
        bearer_token, params, airport_codes, key="originLocationCode"
    ):
        all_flight_offers = []
        for airport_code in airport_codes:
            params[key] = airport_code

            # drop radius parameter for now
            params.pop("radius") if "radius" in params else params
            params["nonStop"] = "false"

            flight_offers = get_flight_offers(bearer_token, params)
            # print(f"Flight offers to {airport_code}: {json.dumps(flight_offers)}")

            all_flight_offers.extend(flight_offers)

        return all_flight_offers

    is_trip_international = check_if_international_trip(
        params["originLocationCode"], params["destinationLocationCode"]
    )

    print(f"Is trip international? {is_trip_international}")

    transit_detailed_flight_offers = []
    if is_trip_international:
        # get all airports in the origin country, except the origin airport
        airport_codes = get_airport_codes_in_country(params["destinationLocationCode"])

        # get all flight offers to those airports
        flight_offers = get_flight_offers_for_airports(
            bearer_token, params, airport_codes, key="destinationLocationCode"
        )
        print(
            f"Flight offers to airports in origin country: {json.dumps(flight_offers)}"
        )

        if flight_offers:
            all_flight_offers.extend(flight_offers)

        # calculate total costs and times for all combinations
        top_3_offers = get_top_3_offers(all_flight_offers)
        print(f"Top 3 offers: {json.dumps(top_3_offers)}")

        
        if top_3_offers:
            transit_detailed_flight_offers = add_transit_options_to_international_flight_itineraries(
                top_3_offers, origin_location_city, destination_location_city
            )

        return transit_detailed_flight_offers
    else:        
        # get all airports in the origin country, except the origin airport
        airport_codes = get_airport_codes_in_country(params["originLocationCode"])
        print(f"Airport codes in origin country: {airport_codes}")

        if params["destinationLocationCode"] in airport_codes:
            airport_codes.remove(params["destinationLocationCode"])

        # get all flight offers to those airports
        flight_offers = get_flight_offers_for_airports(
            bearer_token, params, airport_codes
        )

        all_flight_offers.extend(flight_offers)
        
        print(f"Domestic trip: flight offers lentgh: {len(all_flight_offers)}")

        # calculate top 3 offers
        top_3_offers = get_top_3_offers(all_flight_offers)

        if top_3_offers:
            transit_detailed_flight_offers = add_transit_options_to_domestic_flight_itineraries(
                top_3_offers, origin_location_city, destination_location_city
            )
        
        return top_3_offers    



def store_booking(user, booking_response):
    """
    Store a booking in the database based on the Amadeus API response.

    Args:
        user (User): The authenticated user making the booking.
        booking_response (dict): The raw response JSON from the Amadeus booking API.

    Returns:
        Booking: The created booking instance.

    Raises:
        ValueError: If required fields are missing or the response format is invalid.
    """
    try:
        with transaction.atomic():
            # Extract necessary data
            data = booking_response["data"]
            warnings = booking_response.get("warnings", [])
            travelers_data = data["travelers"]
            contacts_data = data["contacts"]
            flight_offers = data["flightOffers"]
            associated_records = data.get("associatedRecords", [{}])[0]
            price_data = flight_offers[0]["price"]

            # Create travelers
            travelers = []
            for traveler in travelers_data:
                doc = traveler["documents"][0]
                traveler_instance = Traveler.objects.create(
                    first_name=traveler["name"]["firstName"],
                    last_name=traveler["name"]["lastName"],
                    date_of_birth=traveler["dateOfBirth"],
                    passport_number=doc["number"],
                    passport_expiry_date=doc["expiryDate"],
                    passport_issuance_country=doc["issuanceCountry"],
                    nationality=doc["nationality"],
                )
                travelers.append(traveler_instance)

            # Create contacts
            contacts = []
            for contact in contacts_data:
                address = contact["address"]
                contact_instance = Contact.objects.create(
                    email=contact["emailAddress"],
                    addressee_name=contact["addresseeName"]["firstName"],
                    address_lines="\n".join(address["lines"]),
                    postal_code=address["postalCode"],
                    city_name=address["cityName"],
                    country_code=address["countryCode"],
                )
                contacts.append(contact_instance)

            # Create flight segments and itineraries
            itineraries = []
            for itinerary in flight_offers[0]["itineraries"]:
                segments = []
                for segment in itinerary["segments"]:
                    emissions = segment.get("co2Emissions", [{}])[0]
                    segment_instance = FlightSegment.objects.create(
                        departure_iata_code=segment["departure"]["iataCode"],
                        departure_terminal=segment["departure"].get("terminal"),
                        departure_time=segment["departure"]["at"],
                        arrival_iata_code=segment["arrival"]["iataCode"],
                        arrival_terminal=segment["arrival"].get("terminal"),
                        arrival_time=segment["arrival"]["at"],
                        carrier_code=segment["carrierCode"],
                        flight_number=segment["number"],
                        aircraft_code=segment["aircraft"]["code"],
                        duration=segment["duration"],
                        number_of_stops=segment["numberOfStops"],
                        co2_emissions_weight=emissions.get("weight", 0),
                        co2_emissions_unit=emissions.get("weightUnit", ""),
                        cabin=emissions.get("cabin", ""),
                    )
                    segments.append(segment_instance)

                itinerary_instance = Itinerary.objects.create()
                itinerary_instance.segments.set(segments)
                itineraries.append(itinerary_instance)

            # Create price
            taxes = price_data.get("taxes", [])
            price_instance = Price.objects.create(
                currency=price_data["currency"],
                total=price_data["total"],
                base=price_data["base"],
                refundable_taxes=price_data.get("refundableTaxes", 0),
                grand_total=price_data["grandTotal"],
            )

            # Create booking
            booking = Booking.objects.create(
                user=user,
                booking_id=data["id"],
                reference=associated_records["reference"],
                creation_date=associated_records["creationDate"],
                flight_offer_id=associated_records["flightOfferId"],
                price=price_instance,
                ticketing_option=data["ticketingAgreement"]["option"],
            )
            booking.travelers.set(travelers)
            booking.contacts.set(contacts)
            booking.itineraries.set(itineraries)

            # Create warnings
            for warning in warnings:
                Warning.objects.create(
                    booking=booking, title=warning["title"], detail=warning["detail"]
                )

            return booking
    except Exception as e:
        raise ValueError(f"Error storing booking: {e}")