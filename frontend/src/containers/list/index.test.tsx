import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { List } from 'containers/list';

test('Renders List', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <List />
    </TestProviders>
  );
});
