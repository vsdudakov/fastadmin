import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { AsyncTransfer } from 'components/async-transfer';

test('Renders AsyncTransfer', () => {
  const queryClient = new QueryClient();
  const onChange = (data: any) => undefined;
  render(
    <TestProviders client={queryClient}>
      <AsyncTransfer
        idField="id"
        labelField="id"
        parentModel="test"
        onChange={onChange}
        value={undefined}
      />
    </TestProviders>
  );
});
