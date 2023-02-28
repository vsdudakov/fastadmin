import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { List } from 'containers/list';

test('Renders List', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <List />
    </Providers>
  );
});
