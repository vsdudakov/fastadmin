import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { AsyncSelect } from 'components/async-select';

test('Renders AsyncTransfer', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <AsyncSelect idField="id" labelField="id" parentModel="test" />
    </TestProviders>
  );
});
