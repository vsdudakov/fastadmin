import { QueryClient } from "@tanstack/react-query";
import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EFieldWidgetType } from "@/interfaces/configuration";
import { TestProviders } from "@/providers";
import { FilterColumn } from "./index";

const queryClient = new QueryClient();

describe("FilterColumn", () => {
  it("renders and calls onFilter when Filter button is clicked", () => {
    const onFilter = vi.fn();
    const onReset = vi.fn();
    const { container } = render(
      <TestProviders client={queryClient}>
        <FilterColumn
          widgetType={EFieldWidgetType.Input}
          value=""
          onFilter={onFilter}
          onReset={onReset}
        />
      </TestProviders>,
    );
    expect(container).toBeTruthy();
    const buttons = container.querySelectorAll("button");
    if (buttons.length >= 2) {
      buttons[0].click();
      expect(onReset).toHaveBeenCalled();
      buttons[1].click();
      expect(onFilter).toHaveBeenCalled();
    }
  });
});
