import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { UploadInput } from 'components/upload-input';

test('Renders UploadInput', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <UploadInput parentId="test" />
    </TestProviders>
  );
});
