import re

class FlightOfferParser:
    def __init__(self, flight_data):
        self.flight_data = flight_data

    @staticmethod
    def parse_duration(duration_str):
        """Parses ISO 8601 duration strings into a tuple of hours and minutes."""
        match = re.match(r'PT(\d+H)?(\d+M)?', duration_str)
        hours = int(match.group(1)[:-1]) if match.group(1) else 0
        minutes = int(match.group(2)[:-1]) if match.group(2) else 0
        return hours, minutes

    def parse_offers(self):
        offers = []
        for offer in self.flight_data['data']:
            offer_details = {
                'id': offer['id'],
                'price': offer['price']['total'],
                'currency': offer['price']['currency'],
                'itineraries': []
            }
            
            for itinerary in offer['itineraries']:
                hours, minutes = self.parse_duration(itinerary['duration'])
                itinerary_details = {
                    'duration': f'{hours}h {minutes}m',
                    'segments': []
                }
                
                for segment in itinerary['segments']:
                    segment_hours, segment_minutes = self.parse_duration(segment['duration'])
                    segment_details = {
                        'departure': segment['departure']['iataCode'],
                        'arrival': segment['arrival']['iataCode'],
                        'departureTime': segment['departure']['at'],
                        'arrivalTime': segment['arrival']['at'],
                        'carrierCode': segment['carrierCode'],
                        'number': segment['number'],
                        'aircraftCode': segment['aircraft']['code'],
                        'duration': f'{segment_hours}h {segment_minutes}m',
                        'numberOfStops': segment['numberOfStops']
                    }
                    itinerary_details['segments'].append(segment_details)
                
                offer_details['itineraries'].append(itinerary_details)
            
            offers.append(offer_details)
        
        return offers

# The rest of the usage would remain the same.
