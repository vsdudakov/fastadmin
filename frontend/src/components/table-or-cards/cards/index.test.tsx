import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { Cards } from "@/components/table-or-cards/cards";

describe("Cards", () => {
  it("renders loading and empty states", () => {
    const { rerender, container } = render(<Cards loading={true} />);
    expect(container.querySelector(".ant-spin")).toBeTruthy();

    rerender(<Cards dataSource={[]} />);
    expect(container.querySelector(".ant-empty")).toBeTruthy();
  });

  it("renders rows, columns, selection, expansion and pagination", () => {
    const onRowSelectionChange = vi.fn();
    const onTableChange = vi.fn();
    const renderColumn = vi.fn((value: unknown) => `rendered-${String(value)}`);
    const expandedRowRender = vi.fn((record: { id: number; name: string }) => (
      <div>{`expanded-${record.name}`}</div>
    ));

    const { rerender, container } = render(
      <Cards
        rowKey="id"
        className="cards-class"
        dataSource={[{ id: 1, name: "Alice", raw: "RAW" }]}
        columns={[
          { title: "Name", dataIndex: "name", render: renderColumn },
          { title: "Raw", dataIndex: "raw" },
        ]}
        rowSelection={{ selectedRowKeys: [], onChange: onRowSelectionChange }}
        expandable={{
          expandIcon: ({ expanded, onExpand, record }) => (
            <button type="button" onClick={(event) => onExpand(record, event)}>
              {expanded ? "Collapse" : "Expand"}
            </button>
          ),
          expandedRowRender,
        }}
        pagination={{ current: 1, pageSize: 10, total: 20 }}
        onChange={onTableChange}
      />,
    );

    expect(screen.getByText("rendered-Alice")).toBeTruthy();
    expect(screen.getByText("RAW")).toBeTruthy();
    expect(renderColumn).toHaveBeenCalledWith("Alice", {
      id: 1,
      name: "Alice",
      raw: "RAW",
    });

    const checkbox = container.querySelector("input[type='checkbox']");
    expect(checkbox).toBeTruthy();
    if (checkbox) {
      fireEvent.click(checkbox);
      expect(onRowSelectionChange).toHaveBeenCalledWith([1], [], {});
    }

    fireEvent.click(screen.getByRole("button", { name: "Expand" }));
    expect(screen.getByText("expanded-Alice")).toBeTruthy();
    expect(expandedRowRender).toHaveBeenCalledWith(
      { id: 1, name: "Alice", raw: "RAW" },
      0,
      0,
      true,
    );

    fireEvent.click(screen.getByRole("button", { name: "Collapse" }));
    expect(screen.queryByText("expanded-Alice")).toBeNull();

    fireEvent.click(screen.getByTitle("2"));
    expect(onTableChange).toHaveBeenCalledWith(
      { current: 2, pageSize: 10 },
      {},
      {},
      {},
    );

    rerender(
      <Cards
        rowKey="id"
        dataSource={[{ id: 1, name: "Alice", raw: "RAW" }]}
        columns={[{ title: "Raw", dataIndex: "raw" }]}
        rowSelection={{ selectedRowKeys: [1], onChange: onRowSelectionChange }}
      />,
    );

    const selectedCheckbox = container.querySelector("input[type='checkbox']");
    expect(selectedCheckbox).toBeTruthy();
    if (selectedCheckbox) {
      fireEvent.click(selectedCheckbox);
      expect(onRowSelectionChange).toHaveBeenCalledWith([], [], {});
    }
  });

  it("handles rowSelection without onChange callback", () => {
    const { container } = render(
      <Cards
        rowKey="id"
        dataSource={[{ id: 1, name: "Alice" }]}
        columns={[{ title: "Name", dataIndex: "name" }]}
        rowSelection={{ selectedRowKeys: [] }}
      />,
    );

    const checkbox = container.querySelector("input[type='checkbox']");
    expect(checkbox).toBeTruthy();
    if (checkbox) {
      fireEvent.click(checkbox);
    }
  });
});
