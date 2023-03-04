import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { FormContainer } from 'components/form-container';

test('Renders FormContainer', () => {
  const queryClient = new QueryClient();
  const onFinish = (data: any) => undefined;
  render(
    <TestProviders client={queryClient}>
      <FormContainer form="test" onFinish={onFinish} mode="add">
        <div />
      </FormContainer>
    </TestProviders>
  );
});
