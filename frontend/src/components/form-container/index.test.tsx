import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { FormContainer } from 'components/form-container';

test('Renders FormContainer', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <FormContainer form="test" onFinish={(data: any) => {}} mode="add">
        <div />
      </FormContainer>
    </Providers>
  );
});
