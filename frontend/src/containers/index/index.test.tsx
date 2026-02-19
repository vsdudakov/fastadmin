import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { expect, test } from "vitest";

import { Index } from "@/containers/index";
import { TestProviders } from "@/providers";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

test("Renders Index", () => {
  const queryClient = new QueryClient();
  const mockConfig = {
    configuration: {
      site_name: "Admin",
      username_field: "username",
      models: [],
      dashboard_widgets: [],
    },
  };
  const { container } = render(
    <TestProviders client={queryClient}>
      <ConfigurationContext.Provider value={mockConfig}>
        <Index />
      </ConfigurationContext.Provider>
    </TestProviders>,
  );
  expect(container).toBeDefined();
});
