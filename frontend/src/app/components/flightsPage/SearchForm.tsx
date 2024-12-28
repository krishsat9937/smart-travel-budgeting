import { DatePicker, LocalizationProvider } from '@mui/x-date-pickers';
import { cities } from '@/app/data/cities';
import { Autocomplete, Box, FormControl, InputLabel, MenuItem, Select, TextField } from '@mui/material';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import dayjs, { Dayjs } from 'dayjs';
import { useEffect, useState } from 'react';
import CustomButton from './Button';

interface SearchFormProps {
    setSearchParams: (searchParams: any) => void;
}
const SearchForm: React.FC<SearchFormProps> = (props) => {

    const { setSearchParams } = props;
    const [fromValue, setFromValue] = useState(cities[0]);
    const [toValue, setToValue] = useState(cities[1]);
    const [departureValue, setDepartureValue] = useState<Dayjs | null>(dayjs().add(1, 'day'));
    const [arrivalValue, setArrivalValue] = useState<Dayjs | null>(dayjs().add(7, 'day'));
    const [numberOfAdults, setNumberOfAdults] = useState(1);

    useEffect(() => {
        setSearchParams({
            originLocationCode: fromValue?.city || '',
            destinationLocationCode: toValue?.city || '',
            departureDate: departureValue ? departureValue.format('YYYY-MM-DD') : dayjs().format('YYYY-MM-DD'),
            returnDate: arrivalValue ? arrivalValue.format('YYYY-MM-DD') : dayjs().add(7, 'day').format('YYYY-MM-DD'),
            adults: numberOfAdults,
            max: 20,
        });
    }, [fromValue, toValue, departureValue, arrivalValue, numberOfAdults]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        const newSearchParams = {
            originLocationCode: fromValue?.city || '',
            destinationLocationCode: toValue?.city || '',
            departureDate: departureValue ? departureValue.format('YYYY-MM-DD') : dayjs().format('YYYY-MM-DD'),
            returnDate: arrivalValue ? arrivalValue.format('YYYY-MM-DD') : dayjs().add(7, 'day').format('YYYY-MM-DD'),
            adults: numberOfAdults,
            max: 20,
        };
        setSearchParams(newSearchParams);
        console.log('Form submitted', newSearchParams);
    };

    return (
        <LocalizationProvider dateAdapter={AdapterDayjs}>
            <Box component="form" onSubmit={handleSubmit} sx={{ my: 4 }}>
                <Box sx={{ display: 'flex', gap: '1rem' }}>
                    <Autocomplete
                        value={fromValue || ''}
                        onChange={(event, newValue) => {
                            setFromValue(newValue!);
                        }}
                        options={cities}
                        getOptionLabel={(option) => option.city}
                        renderInput={(params) => (
                            <TextField {...params} label="Choose a city" variant="outlined" sx={{ width: '300px' }} />
                        )}
                        renderOption={(props, option) => (
                            <li {...props}>
                                {option.city} ({option.country})
                            </li>
                        )}
                    />
                    <Autocomplete
                        value={toValue || ''}
                        onChange={(event, newValue) => {
                            setToValue(newValue!);
                        }}
                        options={cities}
                        getOptionLabel={(option) => option.city}
                        renderInput={(params) => (
                            <TextField {...params} label="Choose a city" variant="outlined" sx={{ width: '300px' }} />
                        )}
                        renderOption={(props, option) => (
                            <li {...props}>
                                {option.city} ({option.country})
                            </li>
                        )}
                    />
                </Box>
                <br />
                <Box sx={{ display: 'flex', gap: '1rem' }}>
                    <DatePicker
                        label="Departure Date"
                        value={departureValue}
                        onChange={(newValue) => setDepartureValue(newValue)}
                        slots={{
                            textField: TextField,
                        }}
                    />
                    <DatePicker
                        label="Arrival Date"
                        value={arrivalValue}
                        onChange={(newValue) => setArrivalValue(newValue)}
                        slots={{
                            textField: TextField,
                        }}
                    />
                    <FormControl fullWidth>
                        <InputLabel id="number-of-adults-label">Number of Adults</InputLabel>
                        <Select
                            labelId="number-of-adults-label"
                            id="number-of-adults"
                            value={numberOfAdults}
                            label="Number of Adults"
                            onChange={(e) => setNumberOfAdults(e.target.value as number)}
                        >
                            {[...Array(10)].map((_, index) => (
                                <MenuItem key={index + 1} value={index + 1}>
                                    {index + 1}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Box>
                <br />
                <CustomButton type="submit" name="Search" color="primary" />
            </Box>
        </LocalizationProvider>
    );
};

export default SearchForm;
