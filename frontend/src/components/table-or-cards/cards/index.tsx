import {
  Card,
  Checkbox,
  Descriptions,
  Empty,
  Pagination,
  Spin,
  type TableProps,
} from "antd";
import { useState } from "react";

export interface ICards extends Partial<TableProps<any>> {}

export const Cards = (props: ICards) => {
  const [expandedIds, setExpandedIds] = useState<string[]>([]);
  if (props.loading) {
    return <Spin />;
  }
  if (!props.dataSource || props.dataSource.length === 0) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} />;
  }

  const rowKey = props.rowKey as string;

  const onChangePage = (page: number, pageSize: number): void => {
    if (props.onChange) {
      props.onChange(
        {
          current: page,
          pageSize,
        },

        {} as any,

        {} as any,

        {} as any,
      );
    }
  };

  return (
    <>
      {props.dataSource.map((item: any, index: number) => {
        const onSelect = (e: any) => {
          if (!props.rowSelection?.onChange) return;
          if (e.target.checked) {
            const newSelectedRowKeys = [
              ...(props.rowSelection?.selectedRowKeys || []),
              item[rowKey],
            ];

            props.rowSelection?.onChange(newSelectedRowKeys, [], {} as any);
          } else {
            const newSelectedRowKeys = (
              props.rowSelection?.selectedRowKeys || []
            ).filter((pk) => pk !== item[rowKey]);

            props.rowSelection?.onChange(newSelectedRowKeys, [], {} as any);
          }
        };

        return (
          <Card
            key={item[rowKey]}
            className={props.className}
            style={{ marginBottom: 10 }}
          >
            <Descriptions column={1} layout="vertical">
              {props.rowSelection && (
                <Descriptions.Item
                  key="selection"
                  label={<b>Select</b>}
                  contentStyle={{ width: "100%" }}
                >
                  <Checkbox
                    checked={(
                      props.rowSelection?.selectedRowKeys || []
                    ).includes(item[rowKey])}
                    onChange={onSelect}
                  />
                </Descriptions.Item>
              )}
              {props.expandable && (
                <>
                  <Descriptions.Item
                    key="expandable"
                    label={<b>Expand</b>}
                    contentStyle={{ width: "100%" }}
                  >
                    {props.expandable?.expandIcon?.({
                      expanded: expandedIds.includes(item[rowKey]),
                      onExpand: () => {
                        if (expandedIds.includes(item[rowKey])) {
                          setExpandedIds(
                            expandedIds.filter((pk) => pk !== item[rowKey]),
                          );
                        } else {
                          setExpandedIds([...expandedIds, item[rowKey]]);
                        }
                      },
                      record: item,
                    } as any)}
                  </Descriptions.Item>
                  {expandedIds.includes(item[rowKey]) && (
                    <Descriptions.Item
                      key="expandable"
                      contentStyle={{ width: "100%" }}
                    >
                      {props.expandable?.expandedRowRender?.(
                        item,
                        index,
                        0,
                        true,
                      )}
                    </Descriptions.Item>
                  )}
                </>
              )}
              {props.columns?.map((field: any) => (
                <Descriptions.Item
                  key={field.title}
                  label={<b>{field.title}</b>}
                  contentStyle={{ width: "100%" }}
                >
                  {field.render
                    ? field.render(
                        field.dataIndex ? item[field.dataIndex] : item,
                        item,
                      )
                    : item[field.dataIndex]}
                </Descriptions.Item>
              ))}
            </Descriptions>
          </Card>
        );
      })}
      {props.pagination && (
        <Pagination {...props.pagination} onChange={onChangePage} />
      )}
    </>
  );
};
