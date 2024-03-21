import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { FormContainer } from "@/components/form-container";
import { TestProviders } from "@/providers";

test("Renders FormContainer", () => {
  const queryClient = new QueryClient();

  const onFinish = (_data: any) => undefined;
  render(
    <TestProviders client={queryClient}>
      <FormContainer
        modelConfiguration={{
          name: "test",
          permissions: [],
          actions: [],
          fields: [],
        }}
        form="test"
        onFinish={onFinish}
        mode="add"
      >
        <div />
      </FormContainer>
    </TestProviders>,
  );
});
