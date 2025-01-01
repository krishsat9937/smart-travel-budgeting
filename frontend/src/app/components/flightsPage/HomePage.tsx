import React, { useState } from 'react';
import { Container, Box, Typography, Alert } from '@mui/material';
import Header from './Header';
import ResultsGrid from './ResultsGrid';
import SearchForm from './SearchForm';
import CustomButton from './Button';
import { useRouter } from "next/navigation";
import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';
import Tab from '@mui/material/Tab';
import dayjs from 'dayjs';
import useSWR from 'swr';
import { AuthActions } from '@/app/auth/utils';
import { fetcher } from '@/app/fetcher';
import Bookings from '../booking/Bookings';

const HomePage: React.FC = () => {
    const { data: user } = useSWR("/auth/users/me/", fetcher);
    const router = useRouter();
    const [value, setValue] = useState('1');
    const [showBookings, setShowBookings] = useState(false);

    const [searchParams, setSearchParams] = useState({
        originLocationCode: '',
        destinationLocationCode: '',
        departureDate: dayjs().format('YYYY/MM/DD'),
        returnDate: dayjs().add(7, 'day').format('YYYY/MM/DD'),
        adults: 1,
        nonStop: false,
        max: 100
    });

    const handleChange = (event: React.SyntheticEvent, newValue: string) => {
        setValue(newValue);
    };

    const { logout, removeTokens } = AuthActions();

    const handleLogout = () => {
        logout()
            .res(() => {
                removeTokens();
                router.push("/");
            })
            .catch(() => {
                removeTokens();
                router.push("/");
            });
    };

    return (
        <>
            <Container
                fixed
                sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    border: '1px solid black',
                    padding: '1rem',
                    backgroundImage: 'url("/images/smart_travel_app_title_bg.jpeg")',
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                }}
            >
                <Box sx={{ textAlign: 'center' }}>
                    <Header />
                </Box>
                <Typography variant="h1" component="h1" gutterBottom>
                    Welcome to Travel Budgeter {user?.username}!
                </Typography>
                <CustomButton
                    name={showBookings ? "Hide Bookings" : "Your Bookings"}
                    color="primary"
                    onClick={() => setShowBookings(!showBookings)} // Toggle bookings visibility
                />
                <CustomButton
                    name="Logout"
                    color="secondary"
                    onClick={handleLogout}
                />
            </Container>

            {/* Conditionally render search and suggestions */}
            {!showBookings && (
                <>
                    <Container
                        fixed
                        sx={{
                            display: 'flex',
                            justifyContent: 'center',
                            border: '1px solid black',
                            padding: '1rem',
                            backgroundSize: 'cover',
                            backgroundPosition: 'center',
                        }}
                    >
                        <SearchForm setSearchParams={setSearchParams} />
                    </Container>
                    <Container fixed
                        sx={{
                            display: 'flex',
                            justifyContent: 'center',                            
                            padding: '1rem',
                            backgroundSize: 'cover',
                            backgroundPosition: 'center',
                        }}>
                        <Alert severity="info">
                            <strong>Note:</strong> The data displayed on this page is live test data retrieved from the Amadeus API. It may not represent real-world flight prices.
                        </Alert>
                    </Container>

                    <Container fixed>
                        <Box sx={{ width: '100%', typography: 'body1' }}>
                            <TabContext value={value}>
                                <Box sx={{ borderColor: 'divider', p: 1 }}>
                                    <TabList onChange={handleChange} aria-label="lab API tabs example">
                                        <Tab label="Standard Flight Suggestions" value="1" />
                                        <Tab label="Best Travel Suggestions" value="2" />
                                    </TabList>
                                </Box>
                                <TabPanel value="1">
                                    <ResultsGrid searchParams={searchParams} endpoint='flight-offers' />
                                </TabPanel>
                                <TabPanel value="2">
                                    <ResultsGrid searchParams={searchParams} endpoint='best-options' />
                                </TabPanel>
                            </TabContext>
                        </Box>
                    </Container>
                </>
            )}

            {/* Display bookings if showBookings is true */}
            {showBookings && <Bookings />}
        </>
    );
};

export default HomePage;
