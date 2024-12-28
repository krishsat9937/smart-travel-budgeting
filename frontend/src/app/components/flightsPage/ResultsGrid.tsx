import React from 'react';
import { useQuery } from 'react-query';
import FlightsPage from './FlightsPage';

interface ResultsGridProps {
  searchParams: any; // Replace with your search params type  
  endpoint: string;
}

const ResultsGrid: React.FC<ResultsGridProps> = (props: ResultsGridProps) => {
  const { searchParams, endpoint } = props;

  console.log('Search Params:', searchParams);

  // Use the `enabled` flag in useQuery to prevent the query from running until conditions are met
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
        }
      );
      return res.json();
    },
    {
      retry: false,
      // Only enable the query if both origin and destination codes are provided
      enabled: !!searchParams.originLocationCode && !!searchParams.destinationLocationCode,
    }
  );

  // Early return for invalid input
  if (!searchParams.originLocationCode || !searchParams.destinationLocationCode) {
    return <div>Please provide both origin and destination location codes.</div>;
  }

  // Loading state
  if (isLoading) {
    return <div>Loading...</div>;
  }

  // Error state
  if (error) {
    return <div>An error has occurred: {(error as Error).message}</div>;
  }

  // No data state
  if (!data) {
    return <div>No flights found</div>;
  }

  // Success state
  return <FlightsPage flightsData={data} />;
};

export default ResultsGrid;
