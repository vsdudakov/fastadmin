import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { Index } from 'containers/index';

test('Renders Index', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <Index />
    </TestProviders>
  );
});
