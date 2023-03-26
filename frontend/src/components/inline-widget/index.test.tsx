import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { InlineWidget } from 'components/inline-widget';

test('Renders AsyncTransfer', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <InlineWidget
        parentId="test"
        modelConfiguration={{
          name: 'Test',
          fields: [],
          permissions: [],
          actions: [],
          fk_name: 'parent',
        }}
      />
    </TestProviders>
  );
});
