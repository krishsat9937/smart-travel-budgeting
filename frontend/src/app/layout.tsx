'use client';

import { ThemeProvider } from '@mui/material/styles';

import CssBaseline from '@mui/material/CssBaseline';
import { Inter } from "next/font/google";
import { QueryClient, QueryClientProvider } from 'react-query';
import "./styles/global.css";

import theme from './styles/theme';


const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  const queryClient = new QueryClient();

  return (
    <html lang="en">
      <body className={inter.className}>
      <ThemeProvider theme={theme}>
        <QueryClientProvider client={queryClient}>
        <CssBaseline />
          {children}
        </QueryClientProvider>
      </ThemeProvider>
      </body>
    </html>
  );
}
