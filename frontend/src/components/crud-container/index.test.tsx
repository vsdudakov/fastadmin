import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { CrudContainer } from 'components/crud-container';

test('Renders CrudContainer', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <CrudContainer title="test">
        <div />
      </CrudContainer>
    </Providers>
  );
});
