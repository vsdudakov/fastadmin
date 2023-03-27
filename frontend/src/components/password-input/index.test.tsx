import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { PasswordInput } from 'components/password-input';

test('Renders PasswordInput', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <PasswordInput parentId="test" passwordModalForm={true} />
    </TestProviders>
  );
});
