import { Table, type TableProps } from "antd";

import { useIsMobile } from "@/hooks/useIsMobile";

import { Cards } from "./cards";

export interface ITableOrCards extends Partial<TableProps<any>> {}

export const TableOrCards = (props: ITableOrCards) => {
  const isMobile = useIsMobile();
  if (isMobile) {
    return <Cards {...props} />;
  }
  return (
    <Table
      sticky={true}
      scroll={{ x: (props.columns?.length || 0) > 7 ? 1800 : 1200 }}
      {...props}
    />
  );
};
