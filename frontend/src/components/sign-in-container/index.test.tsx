import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { SignInContainer } from 'components/sign-in-container';

test('Renders SignInContainer', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <SignInContainer title="test">
        <div />
      </SignInContainer>
    </TestProviders>
  );
});
