import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { Providers } from 'providers';
import { SignIn } from 'containers/sign-in';

test('Renders SignIn', () => {
  const queryClient = new QueryClient();
  render(
    <Providers client={queryClient}>
      <SignIn />
    </Providers>
  );
});
