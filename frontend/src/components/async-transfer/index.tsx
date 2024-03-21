import { useQuery } from "@tanstack/react-query";
import { Transfer } from "antd";
import type { TransferDirection } from "antd/es/transfer";
import debounce from "lodash.debounce";
import querystring from "query-string";
import type React from "react";
import { useState } from "react";

import { getFetcher } from "@/fetchers/fetchers";
import { useIsMobile } from "@/hooks/useIsMobile";

export interface IAsyncTransfer {
  parentModel: string;
  idField: string;
  labelFields: string[];
  layout?: "horizontal" | "vertical";
  value: string[] | undefined;

  onChange: any;
}

export const AsyncTransfer: React.FC<IAsyncTransfer> = ({
  parentModel,
  idField,
  labelFields,
  layout,
  value,
  onChange,
  ...props
}) => {
  const [search, setSearch] = useState<string | undefined>();
  const isMobile = useIsMobile();

  const queryString = querystring.stringify({
    offset: 0,
    limit: 20,
    search,
  });

  const { data } = useQuery({
    queryKey: [`/list/${parentModel}`, queryString],
    queryFn: () => getFetcher(`/list/${parentModel}?${queryString}`),
  });

  const onFilter = (input: string, option: any) => {
    return (
      ((option?.key as any) || "").toLowerCase().indexOf(input.toLowerCase()) >=
        0 ||
      ((option?.value as any) || "")
        .toLowerCase()
        .indexOf(input.toLowerCase()) >= 0
    );
  };

  const onSearch = (direction: TransferDirection, v: string) => {
    if (direction === "left") {
      setSearch(v);
    }
  };

  const dataSource = (data?.results || []).map((item: any) => {
    const labelField = labelFields.filter((f) => item[f])[0];
    return { key: item[idField], title: item[labelField] };
  });

  const render = (item: any) => item.title;

  return (
    <Transfer
      dataSource={dataSource}
      showSearch={true}
      filterOption={onFilter}
      onSearch={debounce(onSearch, 500)}
      render={render}
      onChange={onChange}
      targetKeys={value}
      listStyle={
        layout === "vertical" || isMobile
          ? { width: "100%", marginTop: 5, marginBottom: 5 }
          : { width: "100%" }
      }
      style={
        layout === "vertical" || isMobile ? { display: "block" } : undefined
      }
      {...props}
    />
  );
};
