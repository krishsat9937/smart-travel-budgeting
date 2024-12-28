// types/FlightOffer.ts
export interface Segment {
    departure: string;
    arrival: string;
    departureTime: string;
    arrivalTime: string;
    carrierCode: string;
    number: string;
    aircraftCode: string;
    duration: string;
    numberOfStops: number;
  }
  
  export interface Itinerary {
    duration: string;
    segments: Segment[];
  }
  
  export interface FlightOffer {
    id: string;
    price: string;
    currency: string;
    itineraries: Itinerary[];
  }

  export interface FlightOfferResults {
    data: FlightOffer[];
  }
  