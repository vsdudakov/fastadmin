import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { TableOrCards } from 'components/table-or-cards';

test('Renders TableOrCards', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <TableOrCards />
    </TestProviders>
  );
});
