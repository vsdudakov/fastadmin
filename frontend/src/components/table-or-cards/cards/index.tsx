import {
  Card,
  Checkbox,
  Descriptions,
  type DescriptionsProps,
  Empty,
  Pagination,
  Spin,
  type TableProps,
} from "antd";
import { useState } from "react";
import { useTranslation } from "react-i18next";

export const Cards = (props: Partial<TableProps<any>>) => {
  const { t: _t } = useTranslation("Cards");
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

        const descriptionItems: NonNullable<DescriptionsProps["items"]> = [];
        if (props.rowSelection) {
          descriptionItems.push({
            key: "selection",
            label: <b>{_t("Select")}</b>,
            children: (
              <Checkbox
                checked={(props.rowSelection?.selectedRowKeys || []).includes(
                  item[rowKey],
                )}
                onChange={onSelect}
              />
            ),
          });
        }
        if (props.expandable) {
          descriptionItems.push({
            key: "expandable",
            label: <b>{_t("Expand")}</b>,
            children: props.expandable?.expandIcon?.({
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
            } as any),
          });
          if (expandedIds.includes(item[rowKey])) {
            descriptionItems.push({
              key: "expanded",
              children: props.expandable?.expandedRowRender?.(
                item,
                index,
                0,
                true,
              ),
            });
          }
        }
        for (const field of props.columns || []) {
          descriptionItems.push({
            key: (field as any).title,
            label: <b>{(field as any).title}</b>,
            children: (field as any).render
              ? (field as any).render(
                  (field as any).dataIndex
                    ? item[(field as any).dataIndex]
                    : item,
                  item,
                )
              : item[(field as any).dataIndex],
          });
        }

        return (
          <Card
            key={item[rowKey]}
            className={props.className}
            style={{ marginBottom: 10 }}
          >
            <Descriptions
              column={1}
              layout="vertical"
              styles={{ content: { width: "100%" } }}
              items={descriptionItems}
            />
          </Card>
        );
      })}
      {props.pagination && (
        <Pagination {...props.pagination} onChange={onChangePage} />
      )}
    </>
  );
};
