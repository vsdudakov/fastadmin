import { act, renderHook } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { EFieldWidgetType, EModelPermission } from "@/interfaces/configuration";
import { useTableColumns } from "./useTableColumns";

vi.mock("react-i18next", async () => {
  const actual =
    await vi.importActual<typeof import("react-i18next")>("react-i18next");
  return {
    ...actual,
    useTranslation: () => ({
      t: (key: string) => key,
      i18n: { changeLanguage: vi.fn() },
    }),
  };
});

vi.mock("@/components/filter-column", () => ({
  FilterColumn: ({
    onFilter,
    onReset,
  }: {
    onFilter: (value: unknown) => void;
    onReset: () => void;
  }) => (
    <div>
      <button
        type="button"
        data-testid="apply-filter"
        onClick={() => onFilter("john")}
      />
      <button type="button" data-testid="reset-filter" onClick={onReset} />
    </div>
  ),
}));

describe("useTableColumns", () => {
  it("returns only actions column when model config is missing", () => {
    const { result } = renderHook(() =>
      useTableColumns(
        undefined,
        undefined,
        vi.fn(),
        vi.fn(),
        vi.fn(),
        vi.fn(),
        vi.fn(),
      ),
    );

    expect(result.current).toHaveLength(1);
    expect(result.current[0].key).toBe("actions");
    expect(result.current[0].title).toBe("Actions");
  });

  it("applies and resets filter from filterDropdown", () => {
    const getFilterValue = vi.fn((name: string) =>
      name === "name" ? "abc" : "",
    );
    const onApplyFilter = vi.fn();
    const onResetFilter = vi.fn();

    const modelConfiguration = {
      name: "User",
      permissions: [],
      actions: [],
      fields: [
        {
          name: "name",
          list_configuration: {
            index: 2,
            empty_value_display: "-",
            filter_widget_type: EFieldWidgetType.Input,
            filter_widget_props: { placeholder: "Filter name" },
          },
        },
        {
          name: "email",
          list_configuration: {
            index: 1,
            empty_value_display: "-",
          },
        },
      ],
    };

    const { result } = renderHook(() =>
      useTableColumns(
        modelConfiguration as any,
        "YYYY-MM-DD HH:mm:ss",
        getFilterValue,
        onApplyFilter,
        onResetFilter,
        vi.fn(),
        vi.fn(),
      ),
    );

    expect(result.current[0].key).toBe("email");
    expect(result.current[1].key).toBe("name");

    const nameColumn = result.current[1];
    const confirm = vi.fn();
    const clearFilters = vi.fn();

    const dropdownElement = nameColumn.filterDropdown({
      confirm,
      clearFilters,
    });

    act(() => {
      dropdownElement.props.onFilter("john");
    });
    expect(onApplyFilter).toHaveBeenCalledWith("name", "john");
    expect(confirm).toHaveBeenCalledTimes(1);

    act(() => {
      dropdownElement.props.onReset();
    });
    expect(onResetFilter).toHaveBeenCalledWith("name");
    expect(clearFilters).toHaveBeenCalledTimes(1);
    expect(confirm).toHaveBeenCalledTimes(2);
  });

  it("renders column values and actions handlers", () => {
    const onDeleteItem = vi.fn();
    const onChangeItem = vi.fn();
    const modelConfiguration = {
      name: "User",
      permissions: [EModelPermission.Delete, EModelPermission.Change],
      actions: [],
      fields: [
        {
          name: "name",
          list_configuration: {
            index: 1,
            empty_value_display: "N/A",
            is_link: true,
          },
        },
        {
          name: "url",
          list_configuration: {
            index: 2,
            empty_value_display: "N/A",
          },
        },
      ],
    };

    const { result } = renderHook(() =>
      useTableColumns(
        modelConfiguration as any,
        undefined,
        vi.fn(),
        vi.fn(),
        vi.fn(),
        onDeleteItem,
        onChangeItem,
      ),
    );

    const linkColumn = result.current.find((c: any) => c.key === "name");
    const urlColumn = result.current.find((c: any) => c.key === "url");
    const actionsColumn = result.current.find((c: any) => c.key === "actions");

    expect(linkColumn.render(undefined, {})).toBe("N/A");

    const linkCell = linkColumn.render("Alice", { id: 1 });
    act(() => {
      linkCell.props.onClick();
    });
    expect(onChangeItem).toHaveBeenCalledWith({ id: 1 });

    const externalLinkCell = urlColumn.render("http://example.com", {});
    expect(externalLinkCell.type).toBe("a");
    expect(externalLinkCell.props.href).toBe("http://example.com");

    expect(urlColumn.render("plain text", {})).toBe("plain text");

    const actionsCell = actionsColumn.render({ id: 99 });
    const actionChildren = actionsCell.props.children;
    act(() => {
      actionChildren[0].props.onConfirm();
      actionChildren[1].props.onClick();
    });
    expect(onDeleteItem).toHaveBeenCalledWith({ id: 99 });
    expect(onChangeItem).toHaveBeenCalledWith({ id: 99 });
  });

  it("uses index fallback sorting and hides actions without permissions", () => {
    const modelConfiguration = {
      name: "User",
      permissions: [],
      actions: [],
      fields: [
        {
          name: "b",
          list_configuration: {
            empty_value_display: "-",
            filter_widget_type: EFieldWidgetType.Input,
          },
        },
        {
          name: "a",
          list_configuration: {
            index: 2,
            empty_value_display: "-",
            filter_widget_type: EFieldWidgetType.Input,
          },
        },
        {
          name: "c",
          list_configuration: {
            empty_value_display: "-",
            filter_widget_type: EFieldWidgetType.Input,
          },
        },
      ],
    };

    const { result } = renderHook(() =>
      useTableColumns(
        modelConfiguration as any,
        undefined,
        () => "",
        vi.fn(),
        vi.fn(),
        vi.fn(),
        vi.fn(),
      ),
    );

    expect(result.current[0].key).toBe("b");
    expect(result.current[1].key).toBe("c");
    expect(result.current[2].key).toBe("a");
    const actionsColumn = result.current.find((c: any) => c.key === "actions");
    const actionsCell = actionsColumn.render({ id: 1 });
    expect(actionsCell.props.children).toHaveLength(2);
    expect(actionsCell.props.children[0]).toBe(false);
    expect(actionsCell.props.children[1]).toBe(false);
  });

  it("uses permission fallback when model configuration is undefined", () => {
    const { result } = renderHook(() =>
      useTableColumns(
        undefined,
        undefined,
        vi.fn(),
        vi.fn(),
        vi.fn(),
        vi.fn(),
        vi.fn(),
      ),
    );
    const actionsColumn = result.current.find((c: any) => c.key === "actions");
    const actionsCell = actionsColumn.render({ id: 10 });
    expect(actionsCell.props.children[0]).toBe(false);
    expect(actionsCell.props.children[1]).toBe(false);
  });
});
