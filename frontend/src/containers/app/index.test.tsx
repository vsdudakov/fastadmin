import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { App } from 'containers/app';

test('Renders App', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <App />
    </Providers>
  );
});
