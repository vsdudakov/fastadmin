import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { Change } from 'containers/change';

test('Renders Change', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <Change />
    </Providers>
  );
});
