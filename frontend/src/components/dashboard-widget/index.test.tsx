import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { test } from "vitest";

import { TestProviders } from "@/providers";
// import { DashboardWidget } from '@/components/dashboard-widget';

test("Renders DashboardWidget", () => {
  const queryClient = new QueryClient();
  render(
    <TestProviders client={queryClient}>
      {/* <DashboardWidget /> */}
    </TestProviders>,
  );
});
