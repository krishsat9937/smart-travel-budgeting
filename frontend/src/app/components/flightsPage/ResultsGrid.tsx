import React, { ReactNode } from 'react';
import { useQuery } from 'react-query';
import FlightsPage from './FlightsPage';

interface ResultsGridProps {
  searchParams: any; // Replace with your search params type  
  endpoint: string;
}

const ResultsGrid: React.FC<ResultsGridProps> = (props: ResultsGridProps): ReactNode => {
  const { searchParams, endpoint } = props;

  console.log('Search Params:', searchParams);

  // Validation: Prevent requests when originLocationCode or destinationLocationCode is empty
  if (!searchParams.originLocationCode || !searchParams.destinationLocationCode) {
    return <div>Please provide both origin and destination location codes.</div>;
  }

  console.log('Search Params:', searchParams);

  const { data, isLoading, error } = useQuery(
    [endpoint, searchParams],
    async () => {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/${endpoint}/`, 
        {
        method: 'POST',
        body: JSON.stringify(searchParams),
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'Authorization': 'Basic YWRtaW46YWRtaW4=',
          'X-CSRFToken': 'lykAelnvoGg9WcYcwSE8GUyFlqFIxJaqp5j7qCp6bpaV7uIqrfmKfEssL0eZnnNU',
        },
      });      
      return res.json();
    },
    {
      retry: false,
      enabled: !!searchParams.originLocationCode && !!searchParams.destinationLocationCode, // Enable query only if both are provided
    }
  );

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!data) {
    return <div>No flights found</div>;
  }

  if (error) {
    return <div>An error has occurred: {(error as Error).message}</div>;
  }

  if (data) {
    return <FlightsPage flightsData={data} />;
  }
};

export default ResultsGrid;
