import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { PhoneNumberInput } from "@/components/phone-number-input";
import { TestProviders } from "@/providers";

test("Renders PhoneInput", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      <PhoneNumberInput />
    </TestProviders>,
  );
});
