import TabContext from '@mui/lab/TabContext';
import TabList from '@mui/lab/TabList';
import TabPanel from '@mui/lab/TabPanel';
import { Box, Container, Typography } from '@mui/material';
import Tab from '@mui/material/Tab';
import dayjs from 'dayjs';
import * as React from 'react';
import { useState } from 'react';
import Header from './Header';
import ResultsGrid from './ResultsGrid';
import SearchForm from './SearchForm';
import CustomButton from './Button';
import { useRouter } from "next/navigation";
import { fetcher } from "@/app/fetcher";
import useSWR from "swr";

import { AuthActions } from '@/app/auth/utils';

const HomePage: React.FC = () => {

    const { data: user } = useSWR("/auth/users/me/", fetcher);

    const router = useRouter();

    const [value, setValue] = useState('1');    

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
                    name="Logout"
                    variant="contained"
                    color="primary"
                    onClick={handleLogout}
                    sx={{ textTransform: 'none' }}
                />
                    
                
            </Container>
            <Container
                fixed
                sx={{
                    display: 'flex',
                    justifyContent: 'center',
                    border: '1px solid black',
                    padding: '1rem',
                    backgroundImage: 'url("https://example.com/second-background.jpg")', // Replace with your second background image URL
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                }}
            >
                <SearchForm  setSearchParams={setSearchParams}/>
            </Container>
            <Container fixed>
                <Box sx={{ width: '100%', typography: 'body1' }}>
                    <TabContext value={value}>
                        <Box sx={{ borderColor: 'divider' , p: 1}}>
                            <TabList onChange={handleChange} aria-label="lab API tabs example">
                                <Tab label="Standard Flight Suggestions" value="1" />
                                <Tab label="Best Travel Suggestions" value="2" />
                            </TabList>
                        </Box>
                        <TabPanel value="1">
                            <ResultsGrid searchParams={searchParams} endpoint='flight-offers'/>
                        </TabPanel>
                        <TabPanel value="2">
                            <ResultsGrid searchParams={searchParams} endpoint='best-options'/>
                        </TabPanel>
                    </TabContext>
                </Box>
            </Container>
        </>
    );
};

export default HomePage;
