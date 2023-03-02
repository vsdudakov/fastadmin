import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { Cards } from 'components/table-or-cards/cards';

test('Renders Cards', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <Cards />
    </Providers>
  );
});
