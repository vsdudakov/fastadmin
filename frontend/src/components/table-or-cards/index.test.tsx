import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { expect, test } from "vitest";

import { TableOrCards } from "@/components/table-or-cards";
import { TestProviders } from "@/providers";

test("Renders TableOrCards", () => {
  const queryClient = new QueryClient();
  const { container } = render(
    <TestProviders client={queryClient}>
      <TableOrCards columns={[]} dataSource={[]} />
    </TestProviders>,
  );
  expect(container.querySelector(".ant-table")).toBeTruthy();
});
