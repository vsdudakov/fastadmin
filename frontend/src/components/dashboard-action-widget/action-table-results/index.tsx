import { SearchOutlined } from "@ant-design/icons";
import {
  Button,
  Col,
  Divider,
  Input,
  Popover,
  Row,
  Space,
  Table,
  theme,
} from "antd";
import type { ColumnsType } from "antd/es/table";
import type React from "react";
import { useMemo, useState } from "react";

import type { IWidgetActionResponse } from "@/interfaces/configuration";

interface ActionTableResultsProps {
  actionResult: IWidgetActionResponse;
  toolbarActions?: React.ReactNode;
}

type TableRow = Record<string, unknown> & { key: string };

const stringifyCellValue = (value: unknown) => {
  if (value === undefined || value === null) {
    return "";
  }
  if (typeof value === "string") {
    return value;
  }
  if (typeof value === "number" || typeof value === "boolean") {
    return String(value);
  }
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
};

export const ActionTableResults: React.FC<ActionTableResultsProps> = ({
  actionResult,
  toolbarActions,
}) => {
  const [columnSearch, setColumnSearch] = useState<Record<string, string>>({});
  const { token } = theme.useToken();

  const dataSource = useMemo<TableRow[]>(
    () =>
      actionResult.data.map((row, index) => ({
        ...(row as Record<string, unknown>),
        key:
          (row as Record<string, unknown>).id?.toString() ||
          (row as Record<string, unknown>).key?.toString() ||
          `${index}`,
      })),
    [actionResult.data],
  );

  const columnKeys = useMemo(() => {
    const keys = new Set<string>();
    for (const row of actionResult.data) {
      for (const key of Object.keys(row as Record<string, unknown>)) {
        keys.add(key);
      }
    }
    return Array.from(keys);
  }, [actionResult.data]);

  const columns = useMemo<ColumnsType<TableRow>>(
    () =>
      columnKeys.map((key) => {
        const uniqueValues = Array.from(
          new Set(
            dataSource
              .map((row) => stringifyCellValue(row[key]))
              .filter((value) => value.length > 0),
          ),
        ).slice(0, 100);

        return {
          key,
          dataIndex: key,
          title: (
            <Space size={4}>
              <span>{key}</span>
              <Popover
                trigger="click"
                placement="bottomLeft"
                content={
                  <div style={{ width: 220 }}>
                    <Input
                      size="small"
                      allowClear
                      autoFocus
                      placeholder={`Search ${key}`}
                      value={columnSearch[key]}
                      onChange={(event) =>
                        setColumnSearch((prev) => ({
                          ...prev,
                          [key]: event.target.value,
                        }))
                      }
                    />
                  </div>
                }
              >
                <Button
                  size="small"
                  type="text"
                  icon={
                    <SearchOutlined
                      style={{
                        color: columnSearch[key]
                          ? token.colorPrimary
                          : undefined,
                      }}
                    />
                  }
                />
              </Popover>
            </Space>
          ),
          filters: uniqueValues.map((value) => ({ text: value, value })),
          filterSearch: true,
          onFilter: (filterValue, row) =>
            stringifyCellValue(row[key]) === String(filterValue),
          sorter: (a, b) =>
            stringifyCellValue(a[key]).localeCompare(
              stringifyCellValue(b[key]),
            ),
          render: (value: unknown) => stringifyCellValue(value),
        };
      }),
    [columnKeys, columnSearch, dataSource, token.colorPrimary],
  );

  const searchedDataSource = useMemo(
    () =>
      dataSource.filter((row) =>
        columnKeys.every((key) => {
          const query = columnSearch[key]?.trim().toLowerCase();
          if (!query) {
            return true;
          }
          return stringifyCellValue(row[key]).toLowerCase().includes(query);
        }),
      ),
    [columnKeys, columnSearch, dataSource],
  );

  return (
    <>
      <Row style={{ marginBottom: 16 }}>
        <Divider />
        <Col xs={24}>
          <Row justify="end">
            <Col>{toolbarActions}</Col>
          </Row>
        </Col>
      </Row>
      <Table
        dataSource={searchedDataSource}
        columns={columns}
        pagination={{ pageSize: 20, showSizeChanger: true }}
        scroll={{ x: "max-content" }}
      />
    </>
  );
};
