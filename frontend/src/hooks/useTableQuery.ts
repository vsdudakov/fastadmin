import { useEffect, useState } from "react";

import type { IInlineModel, IModel } from "@/interfaces/configuration";

const DEFAULT_PAGE = 1;
const DEFAULT_PAGE_SIZE = 10;

interface ITableQuery {
  defaultPage: number;
  defaultPageSize: number;
  page: number;
  setPage: (page: number) => void;
  pageSize: number;
  setPageSize: (pageSize: number) => void;
  search?: string;
  setSearch: (search?: string) => void;
  filters: any;
  setFilters: (filters: any) => void;
  sortBy?: string;
  setSortBy: (sortBy?: string) => void;
  action?: string;
  setAction: (action?: string) => void;
  selectedRowKeys: string[];
  setSelectedRowKeys: (selectedRowKeys: string[]) => void;
  onTableChange: (pagination: any, tableFilters: any, sorter: any) => void;
  resetTable: (preserveFilters?: boolean) => void;
}

export const useTableQuery = (
  modelConfiguration?: IModel | IInlineModel,
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
      setFilters({});
    }
  }, [modelConfiguration?.name]);

  const onTableChange = (
    pagination: any,
    _tableFilters: any,
    sorter: any,
  ): void => {
    if (pagination.pageSize !== pageSize) {
      setPage(DEFAULT_PAGE);
    } else {
      setPage(pagination.current);
    }
    setPageSize(pagination.pageSize);
    if (sorter.field) {
      setSortBy(sorter.order === "ascend" ? sorter.field : `-${sorter.field}`);
    }
  };

  const resetTable = (preserveFilters?: boolean): void => {
    setAction(undefined);
    setSelectedRowKeys([]);
    setPage(DEFAULT_PAGE);
    setPageSize(DEFAULT_PAGE_SIZE);
    setSortBy(undefined);

    if (!preserveFilters) {
      setFilters({});
      setSearch(undefined);
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
    resetTable,
  };
};
