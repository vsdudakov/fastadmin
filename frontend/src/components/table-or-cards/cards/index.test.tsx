import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { Cards } from 'components/table-or-cards/cards';

test('Renders Cards', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <Cards />
    </TestProviders>
  );
});
