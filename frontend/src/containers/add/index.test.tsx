import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';


import { Add } from 'containers/add';

test('Renders Add', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <Add />
    </TestProviders>
  );
});
