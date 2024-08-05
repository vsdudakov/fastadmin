import { PlusCircleOutlined } from "@ant-design/icons";
import { SaveOutlined } from "@ant-design/icons";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Button,
  Col,
  Divider,
  Empty,
  Form,
  Input,
  Modal,
  Row,
  Select,
  Space,
  message,
} from "antd";
import querystring from "query-string";
import type React from "react";
import { useCallback, useContext, useState } from "react";
import { useTranslation } from "react-i18next";

import { ExportBtn } from "@/components/export-btn";
import { FormContainer } from "@/components/form-container";
import { TableOrCards } from "@/components/table-or-cards";
import {
  deleteFetcher,
  getFetcher,
  patchFetcher,
  postFetcher,
} from "@/fetchers/fetchers";
import { handleError } from "@/helpers/forms";
import { getTitleFromModel } from "@/helpers/title";
import {
  transformDataFromServer,
  transformFiltersToServer,
} from "@/helpers/transform";
import { useTableColumns } from "@/hooks/useTableColumns";
import { useTableQuery } from "@/hooks/useTableQuery";
import {
  EModelPermission,
  type IInlineModel,
  type IModelAction,
} from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

export interface IInlineWidget {
  modelConfiguration: IInlineModel;
  parentId: string;
}

export const InlineWidget: React.FC<IInlineWidget> = ({
  modelConfiguration,
  parentId,
}) => {
  const { t: _t } = useTranslation("Inline");
  const [formAdd] = Form.useForm();
  const [formChange] = Form.useForm();

  const { configuration } = useContext(ConfigurationContext);
  const [openList, setOpenList] = useState<boolean>(false);
  const [openAdd, setOpenAdd] = useState<boolean>(false);
  const [openChange, setOpenChange] = useState<any | undefined>();

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
    resetTable,
    onTableChange,
  } = useTableQuery(modelConfiguration);

  const model = modelConfiguration.name;

  const onOpenList = useCallback(() => {
    setOpenList(true);
  }, []);

  const onCloseList = useCallback(() => {
    resetTable();
    setOpenList(false);
  }, [resetTable]);

  const onOpenAdd = useCallback(() => {
    formAdd.resetFields();
    setOpenAdd(true);
    setOpenChange(undefined);
    formAdd.setFieldValue(modelConfiguration.fk_name, parentId);
  }, [formAdd, parentId, modelConfiguration.fk_name]);

  const onCloseAdd = useCallback(() => {
    setOpenAdd(false);
    setOpenChange(undefined);
  }, []);

  const onOpenChange = useCallback(
    (item: any) => {
      formChange.resetFields();
      setOpenChange(item?.id);
      setOpenAdd(false);
    },
    [formChange],
  );

  const onCloseChange = useCallback(() => {
    setOpenChange(undefined);
    setOpenAdd(false);
  }, []);

  const queryString = querystring.stringify({
    search,
    sort_by: sortBy,
    offset: (page - 1) * pageSize,
    limit: pageSize,
    [modelConfiguration.fk_name]: parentId,
    ...transformFiltersToServer(filters),
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: [`/list/${model}`, queryString],
    queryFn: () => getFetcher(`/list/${model}?${queryString}`),
    enabled: openList,
    refetchOnWindowFocus: false,
  });

  const { data: initialChangeValues, isLoading: isLoadingInitialValues } =
    useQuery({
      queryKey: [`/retrieve/${model}/${openChange}`],
      queryFn: () => getFetcher(`/retrieve/${model}/${openChange}`),
      enabled: !!openChange,
      refetchOnWindowFocus: false,
    });

  const {
    mutate: mutateAdd,
    isPending: isLoadingAdd,
    isError: isErrorAdd,
  } = useMutation({
    mutationFn: (data: any) => postFetcher(`/add/${model}`, data),
    onSuccess: () => {
      message.success(_t("Succesfully added"));
      refetch();
      onCloseAdd();
    },
    onError: (error: Error) => {
      handleError(error, formAdd);
    },
  });

  const {
    mutate: mutateChange,
    isPending: isLoadingChange,
    isError: isErrorChange,
  } = useMutation({
    mutationFn: (data: any) =>
      patchFetcher(`/change/${model}/${openChange}`, data),
    onSuccess: () => {
      message.success(_t("Succesfully changed"));
      refetch();
      onCloseChange();
    },
    onError: (error: Error) => {
      handleError(error, formChange);
    },
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
    mutationFn: (data: any) => postFetcher(`/action/${model}/${action}`, data),
    onSuccess: () => {
      resetTable(modelConfiguration?.preserve_filters);
      refetch();
      message.success(_t("Successfully applied"));
    },
    onError: () => {
      message.error(_t("Server error"));
    },
  });

  const onSelectRow = (v: string[]) => setSelectedRowKeys(v);
  const onApplyAction = useCallback(
    () => mutateAction({ ids: selectedRowKeys }),
    [mutateAction, selectedRowKeys],
  );

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
        filters[fieldName] = value;
        setFilters({ ...filters });
        setPage(defaultPage);
        setPageSize(defaultPageSize);
      },
      [defaultPage, defaultPageSize, filters, setFilters, setPage, setPageSize],
    ),
    useCallback(
      (fieldName: string) => {
        // onRemoveFilter
        delete filters[fieldName];
        setFilters({ ...filters });
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
        onOpenChange(record);
      },
      [onOpenChange],
    ),
  );

  const onFinishAdd = (payload: any) => {
    mutateAdd(payload);
  };

  const onFinishChange = (payload: any) => {
    mutateChange(payload);
  };

  const tableHeader = useCallback(
    () => (
      <Row justify="end" gutter={[8, 8]}>
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
        {modelConfiguration?.permissions?.includes(EModelPermission.Export) && (
          <Col>
            <ExportBtn
              model={model}
              search={search}
              filters={{ ...filters, [modelConfiguration.fk_name]: parentId }}
              sortBy={sortBy}
            />
          </Col>
        )}
        {modelConfiguration?.permissions?.includes(EModelPermission.Add) && (
          <Col>
            <Button onClick={onOpenAdd} style={{ marginRight: -10 }}>
              <PlusCircleOutlined /> {_t("Add")}
            </Button>
          </Col>
        )}
      </Row>
    ),
    [
      modelConfiguration?.actions,
      modelConfiguration?.actions_on_top,
      modelConfiguration?.search_fields,
      modelConfiguration?.search_help_text,
      modelConfiguration?.permissions,
      modelConfiguration.fk_name,
      _t,
      action,
      setAction,
      selectedRowKeys.length,
      isLoadingAction,
      onApplyAction,
      setSearch,
      model,
      search,
      filters,
      parentId,
      sortBy,
      onOpenAdd,
    ],
  );

  const tableFooter = useCallback(() => {
    return (
      <>
        {modelConfiguration?.permissions?.includes(EModelPermission.Add) && (
          <Row justify="space-between">
            <Col>
              {(modelConfiguration?.actions || []).length > 0 &&
                modelConfiguration?.actions_on_bottom && (
                  <div style={{ marginLeft: -8 }}>
                    <Select
                      placeholder={_t("Select Action By") as string}
                      allowClear={true}
                      value={action}
                      onChange={setAction}
                      style={{ width: 200 }}
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
                  </div>
                )}
            </Col>
          </Row>
        )}
      </>
    );
  }, [
    _t,
    action,
    isLoadingAction,
    modelConfiguration?.actions,
    modelConfiguration?.actions_on_bottom,
    modelConfiguration?.permissions,
    onApplyAction,
    selectedRowKeys.length,
    setAction,
  ]);

  return (
    <div>
      <Button style={{ minWidth: 200 }} type="dashed" onClick={onOpenList}>
        {_t("Change")}
      </Button>
      <Modal
        width="100%"
        open={openList}
        title={getTitleFromModel(modelConfiguration, true)}
        onCancel={onCloseList}
        footer={null}
      >
        <Row>
          <Col xs={24}>
            <TableOrCards
              title={tableHeader}
              footer={tableFooter}
              loading={isLoading}
              sticky={true}
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
              scroll={{ x: 1000 }}
            />
          </Col>
        </Row>
      </Modal>
      <Modal
        width={600}
        open={openAdd}
        title={`Add ${getTitleFromModel(modelConfiguration)}`}
        onCancel={onCloseAdd}
        footer={null}
      >
        <Divider />
        {modelConfiguration?.permissions.includes(EModelPermission.Add) ? (
          <FormContainer
            modelConfiguration={modelConfiguration}
            form={formAdd}
            onFinish={onFinishAdd}
            mode="inline-add"
            hasOperationError={isErrorAdd}
          >
            <Row justify="end">
              <Col>
                <Space>
                  <Button
                    loading={isLoadingAdd}
                    htmlType="submit"
                    type="primary"
                  >
                    <SaveOutlined /> {_t("Add")}
                  </Button>
                </Space>
              </Col>
            </Row>
          </FormContainer>
        ) : (
          <Empty description={_t("No permissions for model")} />
        )}
      </Modal>
      <Modal
        width={600}
        open={!!openChange}
        title={`Change ${getTitleFromModel(modelConfiguration)} ${openChange}`}
        onCancel={onCloseChange}
        footer={null}
      >
        <Divider />
        {initialChangeValues &&
        modelConfiguration &&
        modelConfiguration.permissions.includes(EModelPermission.Change) ? (
          <FormContainer
            modelConfiguration={modelConfiguration}
            form={formChange}
            onFinish={onFinishChange}
            mode="inline-change"
            hasOperationError={isErrorChange}
            initialValues={transformDataFromServer(initialChangeValues)}
          >
            <Row justify="end">
              <Col>
                <Space>
                  <Button
                    loading={isLoadingChange || isLoadingInitialValues}
                    htmlType="submit"
                    type="primary"
                  >
                    <SaveOutlined /> {_t("Save")}
                  </Button>
                </Space>
              </Col>
            </Row>
          </FormContainer>
        ) : (
          <Empty description={_t("No permissions for model")} />
        )}
      </Modal>
    </div>
  );
};
