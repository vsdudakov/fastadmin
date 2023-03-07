import { IModel, IInlineModel } from 'interfaces/configuration';
import { useState, useEffect } from 'react';

const DEFAULT_PAGE = 1;
const DEFAULT_PAGE_SIZE = 10;

interface ITableQuery {
  defaultPage: number;
  defaultPageSize: number;
  page: number;
  setPage: (page: number) => void;
  pageSize: number;
  setPageSize: (pageSize: number) => void;
  search: string | undefined;
  setSearch: (search: string | undefined) => void;
  filters: any;
  setFilters: (filters: any) => void;
  sortBy: string | undefined;
  setSortBy: (sortBy: string | undefined) => void;
  action: string | undefined;
  setAction: (action: string | undefined) => void;
  selectedRowKeys: string[];
  setSelectedRowKeys: (selectedRowKeys: string[]) => void;
  onTableChange: (pagination: any, tableFilters: any, sorter: any) => void;
}

export const useTableQuery = (
  modelConfiguration: IModel | IInlineModel | undefined
): ITableQuery => {
  const [action, setAction] = useState<string | undefined>();
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

  const [filters, setFilters] = useState<any>({});
  const [search, setSearch] = useState<string | undefined>();
  const [page, setPage] = useState<number>(DEFAULT_PAGE);
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);
  const [sortBy, setSortBy] = useState<string | undefined>();

  useEffect(() => {
    if (modelConfiguration?.list_per_page) {
      setPageSize(modelConfiguration?.list_per_page);
    }
  }, [modelConfiguration?.list_per_page]);

  useEffect(() => {
    if (modelConfiguration?.name) {
      setPage(DEFAULT_PAGE);
      setSortBy(undefined);
    }
  }, [modelConfiguration?.name]);

  const onTableChange = (pagination: any, tableFilters: any, sorter: any): void => {
    if (pagination.pageSize !== pageSize) {
      setPage(DEFAULT_PAGE);
    } else {
      setPage(pagination.current);
    }
    setPageSize(pagination.pageSize);
    if (sorter.field) {
      setSortBy(sorter.order === 'ascend' ? sorter.field : `-${sorter.field}`);
    }
  };

  return {
    defaultPage: DEFAULT_PAGE,
    defaultPageSize: DEFAULT_PAGE_SIZE,
    page,
    setPage,
    pageSize,
    setPageSize,
    search,
    setSearch,
    filters,
    setFilters,
    sortBy,
    setSortBy,
    action,
    setAction,
    selectedRowKeys,
    setSelectedRowKeys,
    onTableChange,
  };
};
