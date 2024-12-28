// src/styles/theme.ts
import { createTheme } from '@mui/material/styles';

// Create a theme instance.
const theme = createTheme({
  palette: {
    primary: {
      main: '#556cd6',
    },
    secondary: {
      main: '#19857b',
    },
    error: {
      main: '#ff5252',
    },
    background: {
      default: '#fff',
    },
  },
  typography: {
    h1: {
      fontSize: '2.2rem',
      fontWeight: 500,
      letterSpacing: '-0.01562em',
    },
    h2: {
      fontSize: '1.8rem',
      fontWeight: 500,
      letterSpacing: '-0.00833em',
    },
    // Continue with other typography styles...
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '4px',
          textTransform: 'none', // Disables uppercase transformation for buttons
          padding: '8px 16px',
          boxShadow: 'none', // Tailwind uses utilities for shadows
          '&:hover': {
            boxShadow: 'none',
          },
        },
      },
    },
  },
});

export default theme;
