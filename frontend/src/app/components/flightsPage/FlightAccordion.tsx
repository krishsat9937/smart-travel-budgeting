import React, { useState } from 'react';
import { Table, TableBody, TableCell, TableContainer, TableRow, IconButton, Box, Typography, Paper } from '@mui/material';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import KeyboardArrowUpIcon from '@mui/icons-material/KeyboardArrowUp';
import { FlightOffer } from '@/app/types/FlightOffer';
import BookNow from '../booking/BookNow';
import { postFetcher } from '@/app/fetcher';

interface FlightAccordionProps {
  searchParams: any;
  flights: FlightOffer[];
}

const FlightAccordion: React.FC<FlightAccordionProps> = ({ searchParams, flights }) => {
  
  // Define the open state for each flight
  const [open, setOpen] = useState<Record<string, boolean>>({});

  // Define the loading state for each flight
  const [loading, setLoading] = useState<Record<string, boolean>>({}); // Ensure this exists


  const handleClick = (id: string) => {
    setOpen(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  const formatTime = (dateString: string): string => {
    return new Date(dateString).toLocaleString([], { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const handleOrder = async (
    flightOffer: FlightOffer,
    bookingDetails: { passengers: any; email: string; address: any }
  ) => {
    
    console.log("final booking params: ", bookingDetails);
    const { passengers, email, address } = bookingDetails;
  
    try {
      // Use the postFetcher to send the request
      const response = await postFetcher("/book-flight/", {
        "flightOffer": flightOffer.rawResponse,
        passengers,
        email,
        address
      });
  
      alert(`Order created successfully: ${response.orderId}`);
    } catch (error) {
      console.error("Error creating order:", error);
      alert("Failed to create order. Please try again later.");
    }
  };
  

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableBody>
          {flights.map((flight) => (
            <React.Fragment key={flight.id}>
              <TableRow sx={{ '& > *': { borderBottom: 'unset' } }}>
                <TableCell>
                  <IconButton size="small" onClick={() => handleClick(flight.id)}>
                    {open[flight.id] ? <KeyboardArrowUpIcon /> : <KeyboardArrowDownIcon />}
                  </IconButton>
                </TableCell>
                <TableCell component="th" scope="row">
                  Flight {flight.id}
                </TableCell>
                {/* <TableCell align="right">{flight.price} {flight.currency}</TableCell> */}
                <TableCell align="right">
                  <BookNow
                    searchParams={searchParams}
                    flightId={flight.id}
                    price={flight.price}
                    currency={flight.currency}
                    flightOffer={flight}
                    handleOrder={handleOrder}
                    isLoading={loading[flight.id] || false}
                  />
                </TableCell>
              </TableRow>
              {open[flight.id] && (
                <TableRow>
                  <TableCell style={{ paddingBottom: 0, paddingTop: 0 }} colSpan={6}>
                    <Box margin={1}>
                      {flight.itineraries.map((itinerary, index) => (
                        <Box key={index} marginBottom={2}>
                          <Typography variant="h6" component="div">Itinerary {index + 1}: {itinerary.duration}</Typography>
                          {itinerary.segments.map((segment, segIndex) => (
                            <Box key={segIndex} marginTop={1}>
                              <Typography>Segment {segIndex + 1}: {segment.departure} to {segment.arrival}</Typography>
                              <Typography>Departure: {formatTime(segment.departureTime)} - Arrival: {formatTime(segment.arrivalTime)}</Typography>
                              <Typography>Flight: {segment.carrierCode}{segment.number}, Aircraft: {segment.aircraftCode}, Stops: {segment.numberOfStops}</Typography>
                            </Box>
                          ))}
                          {itinerary.transit_details && itinerary.transit_details.length > 0 && (
                            <Box marginTop={2}>
                              <Typography variant="h6">Transit Details:</Typography>
                              {itinerary.transit_details.map((transit:any, transitIndex:any) => (
                                <Box key={transitIndex} marginTop={1}>
                                  <Typography>Transit {transitIndex + 1}:</Typography>
                                  <Typography>From: {transit.departure_stop} ({formatTime(transit.departure_time)})</Typography>
                                  <Typography>To: {transit.arrival_stop} ({formatTime(transit.arrival_time)})</Typography>
                                  <Typography>Vehicle: {transit.vehicle}, Line: {transit.line_name}</Typography>
                                  <Typography>Stops: {transit.num_stops}</Typography>
                                  <Typography>Agency: {transit.agency_name} (<a href={transit.agency_url} target="_blank" rel="noopener noreferrer">Details</a>)</Typography>
                                </Box>
                              ))}
                            </Box>
                          )}
                        </Box>
                      ))}
                    </Box>
                  </TableCell>
                </TableRow>
              )}
            </React.Fragment>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default FlightAccordion;
