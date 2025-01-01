import React, { useState } from 'react';
import { Box, Pagination, Typography } from '@mui/material';
import FlightAccordion from './FlightAccordion';


// Assuming FlightOffer is your interface
interface FlightOffer {
    id: string;
    price: string;
    currency: string;
    itineraries: any[];
}

interface FlightsPageProps {
    searchParams: any; // Assuming this prop passes search parameters
    flightsData: FlightOffer[]; // Assuming this prop passes all flights data
}

const FlightsPage: React.FC<FlightsPageProps> = ({ searchParams, flightsData }) => {
    const itemsPerPage = 10;
    const [page, setPage] = useState(1);
    const pageCount = Math.ceil(flightsData.length / itemsPerPage);

    const handleChangePage = (event: React.ChangeEvent<unknown>, newPage: number) => {
        setPage(newPage);
    };

    if (Array.isArray(flightsData) === false) {
        return (
            <Box sx={{ padding: "2rem" }}>
                <Typography variant="h5" component="h1" gutterBottom>
                    Error: {(flightsData as any).error}
                </Typography>
            </Box>
        );
    }
    
    const currentPageData = flightsData?.slice(
        (page - 1) * itemsPerPage,
        page * itemsPerPage
    );

    return (
        <Box sx={{padding: "2rem"}}>
            <Typography variant="h5" component="h1" gutterBottom>
                {`Showing ${currentPageData.length} of ${flightsData.length} results`}
            </Typography>
            <FlightAccordion searchParams={searchParams} flights={currentPageData} />
            <Box display="flex" justifyContent="center" marginTop={4}>
                <Pagination count={pageCount} page={page} onChange={handleChangePage} />
            </Box>
        </Box>
    );
};

export default FlightsPage;
