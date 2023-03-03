import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { FormContainer } from 'components/form-container';

test('Renders FormContainer', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <FormContainer form="test" onFinish={(data: any) => {}} mode="add">
        <div />
      </FormContainer>
    </TestProviders>
  );
});
