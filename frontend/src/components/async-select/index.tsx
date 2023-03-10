import React, { useState } from 'react';
import { Select } from 'antd';
import { useQuery } from '@tanstack/react-query';
import debounce from 'lodash.debounce';
import querystring from 'querystring';
import { getFetcher } from 'fetchers/fetchers';

const { Option } = Select;

export interface IAsyncSelect {
  parentModel: string;
  idField: string;
  labelFields: string[];
}

export const AsyncSelect: React.FC<IAsyncSelect> = ({
  parentModel,
  idField,
  labelFields,
  ...props
}) => {
  const [search, setSearch] = useState<string | undefined>();

  const queryString = querystring.stringify({
    offset: 0,
    limit: 20,
    search,
  });

  const { data, isLoading } = useQuery([`/list/${parentModel}`, queryString], () =>
    getFetcher(`/list/${parentModel}?${queryString}`)
  );

  const onFilter = (input: string, option: any) => {
    return (
      ((option?.key as any) || '').toLowerCase().indexOf(input.toLowerCase()) >= 0 ||
      ((option?.value as any) || '').toLowerCase().indexOf(input.toLowerCase()) >= 0
    );
  };

  const onSearch = (v: string) => {
    setSearch(v);
  };

  return (
    <Select
      showSearch={true}
      loading={isLoading}
      filterOption={onFilter}
      onSearch={debounce(onSearch, 500)}
      {...props}
    >
      {(data?.results || []).map((item: any) => {
        const labelField = labelFields.filter((f) => item[f])[0];
        return <Option key={item[idField]}>{item[labelField]}</Option>;
      })}
    </Select>
  );
};
