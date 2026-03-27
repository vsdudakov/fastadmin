import {
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { ConfigProvider } from "antd";
import { describe, expect, it } from "vitest";

import { ActionTableResults } from "./index";

describe("ActionTableResults", () => {
  it("renders toolbar, column headers and mixed cell values", async () => {
    const circular: Record<string, unknown> = {};
    circular.self = circular;

    render(
      <ConfigProvider>
        <ActionTableResults
          toolbarActions={<button type="button">Export CSV</button>}
          actionResult={{
            data: [
              {
                id: 1,
                name: "alpha",
                active: true,
                amount: 12,
                nullable: null,
                meta: { a: 1 },
                circular,
              },
            ],
          }}
        />
      </ConfigProvider>,
    );

    expect(screen.getByRole("button", { name: "Export CSV" })).toBeTruthy();
    expect((await screen.findAllByText("name")).length).toBeGreaterThan(0);
    expect(screen.getAllByText("alpha").length).toBeGreaterThan(0);
    expect(screen.getAllByText("true").length).toBeGreaterThan(0);
    expect(screen.getAllByText("12").length).toBeGreaterThan(0);
    expect(screen.getAllByText('{"a":1}').length).toBeGreaterThan(0);
    expect(screen.getAllByText("[object Object]").length).toBeGreaterThan(0);
  });

  it("opens column search popover and filters rows", async () => {
    render(
      <ConfigProvider>
        <ActionTableResults
          actionResult={{
            data: [
              { id: 1, name: "alpha", status: "ok" },
              { id: 2, name: "beta", status: "error" },
            ],
          }}
        />
      </ConfigProvider>,
    );

    expect(screen.getAllByText("alpha").length).toBeGreaterThan(0);
    expect(screen.getAllByText("beta").length).toBeGreaterThan(0);

    const nameHeader = screen
      .getAllByRole("columnheader")
      .find((header) => within(header).queryByText("name"));
    expect(nameHeader).toBeTruthy();
    const nameSearchButton = (nameHeader as HTMLElement).querySelector(
      "button",
    );
    expect(nameSearchButton).toBeTruthy();
    fireEvent.click(nameSearchButton as Element);

    const nameSearchInput = await screen.findByPlaceholderText("Search name");
    fireEvent.change(nameSearchInput, { target: { value: "zzz" } });

    await waitFor(() => {
      expect(screen.getAllByText("No data").length).toBeGreaterThan(0);
    });

    fireEvent.change(nameSearchInput, { target: { value: "" } });

    await waitFor(() => {
      expect(screen.getAllByText("alpha").length).toBeGreaterThan(0);
      expect(screen.getAllByText("beta").length).toBeGreaterThan(0);
    });
  });
});
