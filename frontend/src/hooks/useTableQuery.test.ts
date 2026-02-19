import { act, renderHook } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import type { IModel } from "@/interfaces/configuration";
import { useTableQuery } from "./useTableQuery";

const baseModel: IModel = {
  name: "Event",
  fields: [],
  search_fields: [],
  actions: [],
  permissions: [],
};

describe("useTableQuery", () => {
  it("returns default state", () => {
    const { result } = renderHook(() => useTableQuery());
    expect(result.current.page).toBe(1);
    expect(result.current.pageSize).toBe(10);
    expect(result.current.search).toBeUndefined();
    expect(result.current.filters).toEqual({});
    expect(result.current.sortBy).toBeUndefined();
    expect(result.current.selectedRowKeys).toEqual([]);
  });

  it("setPage updates page", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() => result.current.setPage(3));
    expect(result.current.page).toBe(3);
  });

  it("setPageSize updates pageSize", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() => result.current.setPageSize(25));
    expect(result.current.pageSize).toBe(25);
  });

  it("setSearch updates search", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() => result.current.setSearch("foo"));
    expect(result.current.search).toBe("foo");
  });

  it("setFilters updates filters", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() => result.current.setFilters({ name: "test" }));
    expect(result.current.filters).toEqual({ name: "test" });
  });

  it("setSortBy updates sortBy", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() => result.current.setSortBy("-name"));
    expect(result.current.sortBy).toBe("-name");
  });

  it("onTableChange updates page and pageSize", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() =>
      result.current.onTableChange(
        { current: 2, pageSize: 10 },
        {},
        { field: "name", order: "ascend" },
      ),
    );
    expect(result.current.page).toBe(2);
    expect(result.current.pageSize).toBe(10);
    expect(result.current.sortBy).toBe("name");
  });

  it("onTableChange sets sortBy with minus for descend", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() =>
      result.current.onTableChange(
        { current: 1, pageSize: 10 },
        {},
        { field: "name", order: "descend" },
      ),
    );
    expect(result.current.sortBy).toBe("-name");
  });

  it("onTableChange resets page when pageSize changes", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() => result.current.setPage(4));

    act(() =>
      result.current.onTableChange(
        { current: 3, pageSize: 25 },
        {},
        { field: "name", order: "ascend" },
      ),
    );

    expect(result.current.page).toBe(1);
    expect(result.current.pageSize).toBe(25);
  });

  it("onTableChange keeps sortBy unchanged when sorter has no field", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() => result.current.setSortBy("name"));

    act(() =>
      result.current.onTableChange(
        { current: 2, pageSize: 10 },
        {},
        { order: "ascend" },
      ),
    );

    expect(result.current.page).toBe(2);
    expect(result.current.sortBy).toBe("name");
  });

  it("resetTable resets state", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() => {
      result.current.setPage(5);
      result.current.setSearch("x");
      result.current.setFilters({ a: 1 });
    });
    act(() => result.current.resetTable());
    expect(result.current.page).toBe(1);
    expect(result.current.pageSize).toBe(10);
    expect(result.current.search).toBeUndefined();
    expect(result.current.filters).toEqual({});
  });

  it("resetTable with preserveFilters keeps filters and search", () => {
    const { result } = renderHook(() => useTableQuery());
    act(() => {
      result.current.setSearch("x");
      result.current.setFilters({ a: 1 });
    });
    act(() => result.current.resetTable(true));
    expect(result.current.search).toBe("x");
    expect(result.current.filters).toEqual({ a: 1 });
  });

  it("syncs pageSize from modelConfiguration.list_per_page", () => {
    const { result } = renderHook(() =>
      useTableQuery({ ...baseModel, list_per_page: 25 }),
    );
    expect(result.current.pageSize).toBe(25);
  });
});
