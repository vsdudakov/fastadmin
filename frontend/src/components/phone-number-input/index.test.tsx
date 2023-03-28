import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { PhoneNumberInput } from 'components/phone-number-input';

test('Renders PhoneInput', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <PhoneNumberInput />
    </TestProviders>
  );
});
