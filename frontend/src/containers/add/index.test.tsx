import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { Add } from 'containers/add';

test('Renders Add', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <Add />
    </Providers>
  );
});
