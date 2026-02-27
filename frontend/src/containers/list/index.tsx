import { PlusCircleOutlined } from "@ant-design/icons";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Breadcrumb,
  Button,
  Col,
  Empty,
  Input,
  message,
  Row,
  Select,
} from "antd";
import fileDownload from "js-file-download";
import querystring from "query-string";
import type React from "react";
import { useCallback, useContext } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useParams } from "react-router-dom";
import { CrudContainer } from "@/components/crud-container";
import { ExportBtn } from "@/components/export-btn";
import { TableOrCards } from "@/components/table-or-cards";
import { ROUTES } from "@/constants/routes";
import { deleteFetcher, getFetcher, postFetcher } from "@/fetchers/fetchers";
import { getConfigurationModel } from "@/helpers/configuration";
import { handleError } from "@/helpers/forms";
import { getTitleFromModel } from "@/helpers/title";
import { transformFiltersToServer } from "@/helpers/transform";
import { useIsMobile } from "@/hooks/useIsMobile";
import { useTableColumns } from "@/hooks/useTableColumns";
import { useTableQuery } from "@/hooks/useTableQuery";
import {
  EActionResponseType,
  EModelPermission,
  type IActionResponse,
  type IModelAction,
} from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

export const List: React.FC = () => {
  const { configuration } = useContext(ConfigurationContext);
  const navigate = useNavigate();
  const { t: _t } = useTranslation("List");
  const { model } = useParams();
  const isMobile = useIsMobile();

  const modelConfiguration = getConfigurationModel(
    configuration,
    model as string,
  );

  const {
    defaultPage,
    defaultPageSize,
    page,
    setPage,
    pageSize,
    setPageSize,
    search,
    setSearch,
    filters,
    setFilters,
    sortBy,
    action,
    setAction,
    selectedRowKeys,
    setSelectedRowKeys,
    onTableChange,
    resetTable,
  } = useTableQuery(modelConfiguration);

  const queryString = querystring.stringify({
    search,
    sort_by: sortBy,
    offset: (page - 1) * pageSize,
    limit: pageSize,
    ...transformFiltersToServer(filters),
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: [`/list/${model}`, queryString],
    queryFn: () => getFetcher(`/list/${model}?${queryString}`),
    refetchOnWindowFocus: false,
  });

  const { mutate: mutateDelete } = useMutation({
    mutationFn: (id: string) => deleteFetcher(`/delete/${model}/${id}`),
    onSuccess: () => {
      resetTable(modelConfiguration?.preserve_filters);
      refetch();
      message.success(_t("Successfully deleted"));
    },
    onError: (error) => {
      handleError(error);
    },
  });

  const { mutate: mutateAction, isPending: isLoadingAction } = useMutation({
    mutationFn: (payload: any) =>
      postFetcher(`/action/${model}/${action}`, payload),
    onSuccess: (response: IActionResponse) => {
      switch (response?.type) {
        case EActionResponseType.MESSAGE:
          message.success(response.data);
          break;
        case EActionResponseType.DOWNLOAD_BASE64: {
          const fileBase64 = response.data;
          const binaryString = atob(fileBase64);

          const len = binaryString.length;
          const bytes = new Uint8Array(len);
          for (let i = 0; i < len; i += 1) {
            bytes[i] = binaryString.charCodeAt(i);
          }

          const blob = new Blob([bytes], { type: "application/octet-stream" });
          const fileName = response.file_name || "file.bin";

          fileDownload(blob, fileName);
          break;
        }
      }
      resetTable(modelConfiguration?.preserve_filters);
      refetch();
    },
    onError: (response: any) => {
      const detail = response?.response?.data?.detail;
      if (detail) {
        message.error(detail);
      } else {
        message.error(_t("Server error"));
      }
    },
  });

  const onSelectRow = (v: string[]) => setSelectedRowKeys(v);
  const onApplyAction = useCallback(
    () => mutateAction({ ids: selectedRowKeys }),
    [mutateAction, selectedRowKeys],
  );

  const onAdd = useCallback(() => navigate(`/add/${model}`), [model, navigate]);

  const dateTimeFormat = configuration?.datetime_format;
  const columns = useTableColumns(
    modelConfiguration,
    dateTimeFormat,
    useCallback(
      (fieldName: string) => {
        return filters[fieldName];
      },
      [filters],
    ),
    useCallback(
      (fieldName: string, value: any) => {
        // onApplyFilter
        if (
          (Array.isArray(value) && value.length === 0) ||
          value === null ||
          value === undefined
        ) {
          // reset filter
          const rest = { ...filters };
          delete rest[fieldName];
          setFilters(rest);
        } else {
          setFilters({ ...filters, [fieldName]: value });
        }
        setPage(defaultPage);
        setPageSize(defaultPageSize);
      },
      [defaultPage, defaultPageSize, filters, setFilters, setPage, setPageSize],
    ),
    useCallback(
      (fieldName: string) => {
        // onResetFilter
        const rest = { ...filters };
        delete rest[fieldName];
        setFilters(rest);
        setPage(defaultPage);
        setPageSize(defaultPageSize);
      },
      [defaultPage, defaultPageSize, filters, setFilters, setPage, setPageSize],
    ),
    useCallback(
      (record: any) => {
        // onDeleteItem
        mutateDelete(record.id);
      },
      [mutateDelete],
    ),
    useCallback(
      (record: any) => {
        // onChangeItem
        navigate(`/change/${model}/${record.id}`);
      },
      [model, navigate],
    ),
  );

  return (
    <CrudContainer
      title={
        modelConfiguration ? getTitleFromModel(modelConfiguration, true) : ""
      }
      breadcrumbs={
        <Breadcrumb
          items={[
            { title: <Link to={ROUTES.HOME}>{_t("Dashboard")}</Link> },
            {
              title: (
                <Link to={`/list/${model}`}>
                  {modelConfiguration && getTitleFromModel(modelConfiguration)}
                </Link>
              ),
            },
          ]}
        />
      }
      viewOnSite={modelConfiguration?.view_on_site}
      headerActions={
        <Row style={{ marginTop: 10, marginBottom: 10 }} gutter={[8, 8]}>
          {(modelConfiguration?.actions || []).length > 0 &&
            modelConfiguration?.actions_on_top && (
              <Col>
                <Select
                  placeholder={_t("Select Action By") as string}
                  allowClear={true}
                  value={action}
                  onChange={setAction}
                  style={{ width: 300 }}
                >
                  {(modelConfiguration?.actions || []).map(
                    (a: IModelAction) => (
                      <Select.Option key={a.name} value={a.name}>
                        {a.description || a.name}
                      </Select.Option>
                    ),
                  )}
                </Select>
                <Button
                  disabled={!action || selectedRowKeys.length === 0}
                  style={{ marginLeft: 5 }}
                  loading={isLoadingAction}
                  onClick={onApplyAction}
                >
                  {_t("Apply")}
                </Button>
              </Col>
            )}
          {(modelConfiguration?.search_fields || []).length > 0 && (
            <Col>
              <Input.Search
                placeholder={
                  modelConfiguration?.search_help_text ||
                  (_t("Search By") as string)
                }
                allowClear={true}
                onSearch={setSearch}
                style={{ width: 200 }}
              />
            </Col>
          )}
          {modelConfiguration?.permissions?.includes(
            EModelPermission.Export,
          ) && (
            <Col>
              <ExportBtn
                model={model}
                search={search}
                filters={filters}
                sortBy={sortBy}
              />
            </Col>
          )}
          {modelConfiguration?.permissions?.includes(EModelPermission.Add) && (
            <Col>
              <Button onClick={onAdd}>
                <PlusCircleOutlined /> {_t("Add")}
              </Button>
            </Col>
          )}
        </Row>
      }
      bottomActions={
        (modelConfiguration?.actions || []).length > 0 &&
        modelConfiguration?.actions_on_bottom && (
          <div style={{ marginTop: isMobile ? 10 : -50 }}>
            <Select
              placeholder={_t("Select Action By") as string}
              allowClear={true}
              value={action}
              onChange={setAction}
              style={{ width: 200 }}
            >
              {(modelConfiguration?.actions || []).map((a: IModelAction) => (
                <Select.Option key={a.name} value={a.name}>
                  {a.description || a.name}
                </Select.Option>
              ))}
            </Select>
            <Button
              disabled={!action || selectedRowKeys.length === 0}
              style={{ marginLeft: 5 }}
              loading={isLoadingAction}
              onClick={onApplyAction}
            >
              {_t("Apply")}
            </Button>
          </div>
        )
      }
    >
      {modelConfiguration ? (
        <TableOrCards
          loading={isLoading}
          rowSelection={
            (modelConfiguration?.actions || []).length > 0
              ? {
                  selectedRowKeys,
                  onChange: onSelectRow as any,
                }
              : undefined
          }
          columns={columns}
          onChange={onTableChange}
          rowKey="id"
          dataSource={data?.results || []}
          pagination={{
            current: page,
            pageSize,
            total: data?.total,
            showSizeChanger: true,
          }}
        />
      ) : (
        <Empty description={_t("No permissions for model")} />
      )}
    </CrudContainer>
  );
};
