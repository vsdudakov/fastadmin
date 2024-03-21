import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { UploadInput } from "@/components/upload-input";
import { TestProviders } from "@/providers";

test("Renders UploadInput", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <UploadInput parentId="test" />
    </TestProviders>,
  );
});
