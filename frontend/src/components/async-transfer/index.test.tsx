import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { AsyncTransfer } from "@/components/async-transfer";
import { TestProviders } from "@/providers";

test("Renders AsyncTransfer", () => {
  const queryClient = new QueryClient();

  const onChange = (_data: any) => undefined;
  render(
    <TestProviders client={queryClient}>
      <AsyncTransfer
        idField="id"
        labelFields={["id"]}
        parentModel="test"
        onChange={onChange}
        value={undefined}
      />
    </TestProviders>,
  );
});
