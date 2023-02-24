import React, { useState } from 'react';
import { Spin, Card, Pagination, Descriptions, Empty, TableProps } from 'antd';

export interface ICards extends Partial<TableProps<any>> {}

export const Cards = (props: ICards) => {
  const [expandedIds, setExpandedIds] = useState<string[]>([]);
  if (props.loading) {
    return <Spin />;
  }
  if (!props.dataSource || props.dataSource.length === 0) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} />;
  }

  const onChangePage = (page: number, pageSize: number): void => {
    if (props.onChange) {
      props.onChange(
        {
          current: page,
          pageSize,
        },
        {} as any,
        {} as any,
        {} as any
      );
    }
  };
  return (
    <>
      {props.dataSource.map((item: any, index: number) => (
        <Card key={index} className={props.className} style={{ marginBottom: 10 }}>
          <Descriptions column={1} layout="vertical">
            {props.expandable && (
              <>
                <Descriptions.Item key="expandable" label="Expand" contentStyle={{ width: '100%' }}>
                  {props.expandable &&
                    props.expandable.expandIcon &&
                    props.expandable.expandIcon({
                      expanded: expandedIds.includes(item.pk),
                      onExpand: () => {
                        if (expandedIds.includes(item.pk)) {
                          setExpandedIds(expandedIds.filter((pk) => pk !== item.pk));
                        } else {
                          setExpandedIds([...expandedIds, item.pk]);
                        }
                      },
                      record: item,
                    } as any)}
                </Descriptions.Item>
                {expandedIds.includes(item.pk) && (
                  <Descriptions.Item key="expandable" contentStyle={{ width: '100%' }}>
                    {props.expandable &&
                      props.expandable.expandedRowRender &&
                      props.expandable.expandedRowRender(item, index, 0, true)}
                  </Descriptions.Item>
                )}
              </>
            )}
            {props.columns?.map((field: any) => (
              <Descriptions.Item
                key={field.title}
                label={<b>{field.title}</b>}
                contentStyle={{ width: '100%' }}
              >
                {field.render
                  ? field.render(field.dataIndex ? item[field.dataIndex] : item, item)
                  : item[field.dataIndex]}
              </Descriptions.Item>
            ))}
          </Descriptions>
        </Card>
      ))}
      {props.pagination && <Pagination {...props.pagination} onChange={onChangePage} />}
    </>
  );
};
