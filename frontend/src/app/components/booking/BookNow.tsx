import React, { useState } from 'react';
import { Button, CircularProgress } from '@mui/material';
import BookingForm from './BookingForm';

interface BookNowProps {
  searchParams: any;
  flightId: string;
  price: string;
  currency: string;
  flightOffer: any;
  handleOrder: (flightOffer: any, passengerDetails: any) => Promise<void>;
  isLoading: boolean;
}

const BookNow: React.FC<BookNowProps> = ({ searchParams, flightId, price, currency, flightOffer, handleOrder, isLoading }) => {

  console.log("search params: ", searchParams);

  const [formOpen, setFormOpen] = useState(false);

  const handleBooking = async (passengerDetails: any) => {
    console.log("Booking flight with details: ", passengerDetails);
    await handleOrder(flightOffer, passengerDetails);
  };

  return (
    <>
      <Button
        variant="contained"
        color="primary"
        onClick={() => setFormOpen(true)}
        disabled={isLoading}
      >
        {isLoading ? <CircularProgress size={20} /> : `Book Now (${price} ${currency})`}
      </Button>
      <BookingForm
        open={formOpen}
        onClose={() => setFormOpen(false)}
        onSubmit={handleBooking}
        numPassengers={searchParams.adults} // Pass the number of adults as a prop
      />
    </>
  );
};

export default BookNow;
