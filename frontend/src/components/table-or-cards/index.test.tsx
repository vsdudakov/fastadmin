import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { TableOrCards } from 'components/table-or-cards';

test('Renders TableOrCards', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <TableOrCards />
    </Providers>
  );
});
