import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { JsonTextArea } from 'components/json-textarea';

test('Renders JsonTextArea', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <JsonTextArea />
    </TestProviders>
  );
});
