import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient } from '@tanstack/react-query';

import { TestProviders } from 'providers';
import { TextEditor } from 'components/texteditor-field';

test('Renders TextEditor', () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <TextEditor />
    </TestProviders>
  );
});
