import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { TextEditor } from "@/components/texteditor-field";
import { TestProviders } from "@/providers";

test("Renders TextEditor", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <TextEditor />
    </TestProviders>,
  );
});
