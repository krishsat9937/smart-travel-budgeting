import React, { useState } from 'react';
import { Modal, Box, TextField, Button, Typography, Grid } from '@mui/material';

interface PassengerDetails {
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  passportNumber: string;
  passportExpiryDate: string; // New field
}

interface Address {
  lines: string[];
  postalCode: string;
  city: string;
  countryCode: string;
}

interface BookingFormProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (details: {
    passengers: PassengerDetails[];
    email: string;
    address: Address;
  }) => void;
  numPassengers: number;
}
  
  const BookingForm: React.FC<BookingFormProps> = ({
    open,
    onClose,
    onSubmit,
    numPassengers,
  }) => {
    const [passengers, setPassengers] = useState<PassengerDetails[]>(
      Array.from({ length: numPassengers }, () => ({
        firstName: '',
        lastName: '',
        dateOfBirth: '',
        passportNumber: '',
        passportExpiryDate: '',
      }))
    );
  
    const [email, setEmail] = useState<string>('');
    const [address, setAddress] = useState<Address>({
      lines: [''], // Initialize with an empty array
      postalCode: '',
      city: '',
      countryCode: '',
    });
  
    const handlePassengerChange = (
      index: number,
      field: keyof PassengerDetails,
      value: string
    ) => {
      setPassengers((prev) => {
        const updated = [...prev];
        updated[index] = { ...updated[index], [field]: value };
        return updated;
      });
    };
  
    const handleAddressChange = (field: keyof Address, value: string | string[]) => {
      setAddress((prev) => ({
        ...prev,
        [field]: value,
      }));
    };
  
    const handleAddAddressLine = () => {
      setAddress((prev) => ({
        ...prev,
        lines: [...prev.lines, ''],
      }));
    };
  
    const handleRemoveAddressLine = (index: number) => {
      setAddress((prev) => ({
        ...prev,
        lines: prev.lines.filter((_, i) => i !== index),
      }));
    };
  
    const handleAddressLineChange = (index: number, value: string) => {
      setAddress((prev) => {
        const updatedLines = [...prev.lines];
        updatedLines[index] = value;
        return {
          ...prev,
          lines: updatedLines,
        };
      });
    };
  
    const handleSubmit = () => {
      if (
        !email ||
        passengers.some((p) => !p.firstName || !p.passportNumber || !p.passportExpiryDate) ||
        address.lines.length === 0 || // Ensure at least one address line exists
        !address.city ||
        !address.postalCode ||
        !address.countryCode
      ) {
        alert('Please fill in all required fields!');
        return;
      }
      onSubmit({ passengers, email, address });
      onClose();
    };
  
    return (
      <Modal open={open} onClose={onClose}>
        <Box
          sx={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            width: 600,
            bgcolor: 'background.paper',
            boxShadow: 24,
            p: 4,
            borderRadius: 2,
          }}
        >
          <Typography variant="h6" component="h2" gutterBottom>
            Booking Details
          </Typography>
  
          {/* Email Field */}
          <Box mb={3}>
            <TextField
              fullWidth
              margin="normal"
              label="Email for Communication"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </Box>
  
          {/* Passenger Details */}
          {passengers.map((passenger, index) => (
            <Box key={index} mb={3}>
              <Typography variant="subtitle1">Passenger {index + 1}</Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="First Name"
                    value={passenger.firstName}
                    onChange={(e) =>
                      handlePassengerChange(index, 'firstName', e.target.value)
                    }
                    required
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Last Name"
                    value={passenger.lastName}
                    onChange={(e) =>
                      handlePassengerChange(index, 'lastName', e.target.value)
                    }
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Date of Birth"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={passenger.dateOfBirth}
                    onChange={(e) =>
                      handlePassengerChange(index, 'dateOfBirth', e.target.value)
                    }
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Passport Number"
                    value={passenger.passportNumber}
                    onChange={(e) =>
                      handlePassengerChange(index, 'passportNumber', e.target.value)
                    }
                    required
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label="Passport Expiry Date"
                    type="date"
                    InputLabelProps={{ shrink: true }}
                    value={passenger.passportExpiryDate}
                    onChange={(e) =>
                      handlePassengerChange(index, 'passportExpiryDate', e.target.value)
                    }
                    required
                  />
                </Grid>
              </Grid>
            </Box>
          ))}
  
          {/* Address Details */}
          <Box mb={3}>
            <Typography variant="subtitle1">Contact Address</Typography>
            <Grid container spacing={2}>
              {address.lines.map((line, index) => (
                <Grid item xs={12} key={index}>
                  <TextField
                    fullWidth
                    margin="normal"
                    label={`Address Line ${index + 1}`}
                    value={line}
                    onChange={(e) => handleAddressLineChange(index, e.target.value)}
                    required
                  />
                  {index > 0 && (
                    <Button
                      onClick={() => handleRemoveAddressLine(index)}
                      color="error"
                      size="small"
                    >
                      Remove
                    </Button>
                  )}
                </Grid>
              ))}
              {/* <Button onClick={handleAddAddressLine} size="small">
                Add Address Line
              </Button> */}
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  margin="normal"
                  label="Postal Code"
                  value={address.postalCode}
                  onChange={(e) => handleAddressChange('postalCode', e.target.value)}
                  required
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  margin="normal"
                  label="City"
                  value={address.city}
                  onChange={(e) => handleAddressChange('city', e.target.value)}
                  required
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  margin="normal"
                  label="Country Code"
                  value={address.countryCode}
                  onChange={(e) => handleAddressChange('countryCode', e.target.value)}
                  required
                />
              </Grid>
            </Grid>
          </Box>
  
          {/* Submit and Cancel Buttons */}
          <Box display="flex" justifyContent="space-between" mt={2}>
            <Button variant="outlined" onClick={onClose}>
              Cancel
            </Button>
            <Button variant="contained" onClick={handleSubmit}>
              Submit
            </Button>
          </Box>
        </Box>
      </Modal>
    );
  };
  
  export default BookingForm;