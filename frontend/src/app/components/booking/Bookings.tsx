import React, { useState, useEffect } from 'react';
import {
    Container,
    Typography,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
} from '@mui/material';
import { fetcher } from '@/app/fetcher';

interface Traveler {
    first_name: string;
    last_name: string;
    date_of_birth: string;
    passport_number: string;
    passport_expiry_date: string;
    passport_issuance_country: string;
    nationality: string;
}

interface Contact {
    email: string;
    addressee_name: string;
    address_lines: string;
    postal_code: string;
    city_name: string;
    country_code: string;
}

interface Segment {
    departure_iata_code: string;
    departure_terminal: string;
    departure_time: string;
    arrival_iata_code: string;
    arrival_terminal: string;
    arrival_time: string;
    carrier_code: string;
    flight_number: string;
    aircraft_code: string;
    duration: string;
    number_of_stops: number;
    co2_emissions_weight: number;
    co2_emissions_unit: string;
    cabin: string;
}

interface Booking {
    id: number;
    booking_id: string;
    reference: string;
    creation_date: string;
    travelers: Traveler[];
    contacts: Contact[];
    itineraries: { segments: Segment[] }[];
    price: {
        currency: string;
        total: number;
        base: number;
        refundable_taxes: number;
        grand_total: number;
    };
    ticketing_option: string;
}

const Bookings: React.FC = () => {
    const [bookings, setBookings] = useState<Booking[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchBookings = async () => {
            try {
                const response = await fetcher('/bookings');
                setBookings(response);
            } catch (err) {
                setError('An error occurred while fetching bookings.');
            } finally {
                setLoading(false);
            }
        };

        fetchBookings();
    }, []);

    if (loading) {
        return (
            <Container>
                <Typography variant="h6">Loading bookings...</Typography>
            </Container>
        );
    }

    if (error) {
        return (
            <Container>
                <Typography variant="h6" color="error">
                    {error}
                </Typography>
            </Container>
        );
    }

    return (
        <Container fixed>
            <Typography variant="h4" sx={{ marginBottom: 2, p:5 }}>
                Your Bookings
            </Typography>
            {bookings.length > 0 ? (
                <TableContainer component={Paper}>
                    <Table>
                        <TableHead>
                            <TableRow>
                                <TableCell>
                                    <Typography fontWeight="bold">Booking ID</Typography>
                                </TableCell>
                                <TableCell>
                                    <Typography fontWeight="bold">Reference</Typography>
                                </TableCell>
                                <TableCell>
                                    <Typography fontWeight="bold">Traveler</Typography>
                                </TableCell>
                                <TableCell>
                                    <Typography fontWeight="bold">Contact</Typography>
                                </TableCell>
                                <TableCell>
                                    <Typography fontWeight="bold">Price</Typography>
                                </TableCell>
                                <TableCell>
                                    <Typography fontWeight="bold">Itinerary</Typography>
                                </TableCell>
                                <TableCell>
                                    <Typography fontWeight="bold">Ticketing Option</Typography>
                                </TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {bookings.map((booking) => (
                                <TableRow key={booking.id}>
                                    <TableCell>{booking.booking_id}</TableCell>
                                    <TableCell>{booking.reference}</TableCell>
                                    <TableCell>
                                        {booking.travelers.map((traveler, index) => (
                                            <div key={index}>
                                                {traveler.first_name} {traveler.last_name} <br />
                                                DOB: {traveler.date_of_birth} <br />
                                                Passport: {traveler.passport_number} ({traveler.nationality})
                                            </div>
                                        ))}
                                    </TableCell>
                                    <TableCell>
                                        {booking.contacts.map((contact, index) => (
                                            <div key={index}>
                                                {contact.addressee_name} <br />
                                                {contact.email} <br />
                                                {contact.address_lines}, {contact.city_name}, {contact.postal_code},{' '}
                                                {contact.country_code}
                                            </div>
                                        ))}
                                    </TableCell>
                                    <TableCell>
                                        Total: {booking.price.currency} {booking.price.total} <br />
                                        Base: {booking.price.base} <br />
                                        Refundable Taxes: {booking.price.refundable_taxes}
                                    </TableCell>
                                    <TableCell>
                                        {booking.itineraries.map((itinerary, i) =>
                                            itinerary.segments.map((segment, j) => (
                                                <div key={`${i}-${j}`}>
                                                    {segment.departure_iata_code} (
                                                    {segment.departure_terminal}) →
                                                    {segment.arrival_iata_code} ({segment.arrival_terminal}) <br />
                                                    Time: {new Date(segment.departure_time).toLocaleString()} →{' '}
                                                    {new Date(segment.arrival_time).toLocaleString()} <br />
                                                    Carrier: {segment.carrier_code} {segment.flight_number} <br />
                                                    Cabin: {segment.cabin}, Stops: {segment.number_of_stops} <br />
                                                    CO2: {segment.co2_emissions_weight}{' '}
                                                    {segment.co2_emissions_unit}
                                                </div>
                                            ))
                                        )}
                                    </TableCell>
                                    <TableCell>{booking.ticketing_option}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            ) : (
                <Typography>No bookings found.</Typography>
            )}
        </Container>
    );
};

export default Bookings;
