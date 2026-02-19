import { act, render, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { AsyncTransfer } from "./index";

const { mockUseQuery, mockUseIsMobile, transferPropsRef } = vi.hoisted(() => ({
  mockUseQuery: vi.fn(),
  mockUseIsMobile: vi.fn(),
  transferPropsRef: { current: undefined as any },
}));

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => mockUseQuery(options),
}));

vi.mock("lodash.debounce", () => ({
  default: (fn: (...args: any[]) => any) => fn,
}));

vi.mock("@/hooks/useIsMobile", () => ({
  useIsMobile: () => mockUseIsMobile(),
}));

vi.mock("antd", () => ({
  Transfer: (props: any) => {
    transferPropsRef.current = props;
    return <div data-testid="transfer">{props.dataSource.length}</div>;
  },
}));

describe("AsyncTransfer", () => {
  it("maps datasource, filters and updates search only for left direction", async () => {
    mockUseIsMobile.mockReturnValue(false);
    mockUseQuery.mockReturnValue({
      data: {
        results: [
          { id: "1", name: "Alpha" },
          { id: "2", title: "Beta" },
        ],
      },
    });

    render(
      <AsyncTransfer
        idField="id"
        labelFields={["name", "title"]}
        parentModel="users"
        onChange={vi.fn()}
        value={["1"]}
        layout="vertical"
      />,
    );

    expect(transferPropsRef.current.dataSource).toEqual([
      { key: "1", title: "Alpha" },
      { key: "2", title: "Beta" },
    ]);
    expect(transferPropsRef.current.render({ title: "X" })).toBe("X");
    expect(transferPropsRef.current.filterOption("alp", { key: "Alpha" })).toBe(
      true,
    );
    expect(
      transferPropsRef.current.filterOption("bet", { key: "z", value: "Beta" }),
    ).toBe(true);
    expect(
      transferPropsRef.current.filterOption("qqq", { key: "a", value: "b" }),
    ).toBe(false);
    expect(transferPropsRef.current.listStyle).toEqual({
      width: "100%",
      marginTop: 5,
      marginBottom: 5,
    });
    expect(transferPropsRef.current.style).toEqual({ display: "block" });

    act(() => {
      transferPropsRef.current.onSearch("right", "should-not-apply");
    });
    let lastQuery = mockUseQuery.mock.calls[
      mockUseQuery.mock.calls.length - 1
    ]?.[0] as any;
    expect(lastQuery.queryKey[1]).not.toContain("should-not-apply");

    act(() => {
      transferPropsRef.current.onSearch("left", "john");
    });
    await waitFor(() => {
      lastQuery = mockUseQuery.mock.calls[
        mockUseQuery.mock.calls.length - 1
      ]?.[0] as any;
      expect(lastQuery.queryKey[1]).toContain("search=john");
    });
  });

  it("uses non-mobile horizontal styles", () => {
    mockUseIsMobile.mockReturnValue(false);
    mockUseQuery.mockReturnValue({ data: { results: [] } });

    render(
      <AsyncTransfer
        idField="id"
        labelFields={["name"]}
        parentModel="users"
        onChange={vi.fn()}
        value={undefined}
        layout="horizontal"
      />,
    );

    expect(transferPropsRef.current.listStyle).toEqual({ width: "100%" });
    expect(transferPropsRef.current.style).toBeUndefined();
  });
});
