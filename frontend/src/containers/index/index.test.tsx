import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { Index } from 'containers/index';

test('Renders Index', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <Index />
    </Providers>
  );
});
