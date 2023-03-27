import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { ExportBtn } from 'components/export-btn';

test('Renders ExportBtn', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <ExportBtn />
    </TestProviders>
  );
});
