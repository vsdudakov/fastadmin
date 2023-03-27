import React, { useCallback, useContext, useState } from 'react';
import { Button, Col, Divider, Empty, Form, Input, message, Modal, Row, Select, Space } from 'antd';
import { PlusCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import querystring from 'querystring';
import { useMutation, useQuery } from '@tanstack/react-query';
import { SaveOutlined } from '@ant-design/icons';

import { TableOrCards } from 'components/table-or-cards';
import { useTableQuery } from 'hooks/useTableQuery';
import { useTableColumns } from 'hooks/useTableColumns';
import { handleError } from 'helpers/forms';
import { transformDataFromServer, transformFiltersToServer } from 'helpers/transform';
import { deleteFetcher, getFetcher, patchFetcher, postFetcher } from 'fetchers/fetchers';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { EModelPermission, IInlineModel, IModelAction } from 'interfaces/configuration';
import { getTitleFromModelClass } from 'helpers/title';
import { ExportBtn } from 'components/export-btn';
import { FormContainer } from 'components/form-container';

export interface IInlineWidget {
  modelConfiguration: IInlineModel;
  parentId: string;
}

export const InlineWidget: React.FC<IInlineWidget> = ({ modelConfiguration, parentId }) => {
  const { t: _t } = useTranslation('Inline');
  const { configuration } = useContext(ConfigurationContext);
  const [openList, setOpenList] = useState<boolean>(false);
  const [openAdd, setOpenAdd] = useState<boolean>(false);
  const [openChange, setOpenChange] = useState<any | undefined>();

  const [formAdd] = Form.useForm();
  const [formChange] = Form.useForm();

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
    formAdd.setFieldValue(modelConfiguration.fk_name, parentId);
    setOpenAdd(true);
    setOpenChange(undefined);
  }, [formAdd, parentId, modelConfiguration.fk_name]);

  const onCloseAdd = useCallback(() => {
    setOpenAdd(false);
    setOpenChange(undefined);
  }, []);

  const onOpenChange = useCallback(
    (item: any) => {
      formChange.resetFields();
      formChange.setFieldValue(modelConfiguration.fk_name, parentId);
      formChange.setFieldsValue(transformDataFromServer(item));
      setOpenChange(item);
      setOpenAdd(false);
    },
    [formChange, parentId, modelConfiguration.fk_name]
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

  const { data, isLoading, refetch } = useQuery(
    [`/list/${model}`, queryString],
    () => getFetcher(`/list/${model}?${queryString}`),
    {
      enabled: openList,
      refetchOnWindowFocus: false,
    }
  );

  const {
    mutate: mutateAdd,
    isLoading: isLoadingAdd,
    isError: isErrorAdd,
  } = useMutation((payload: any) => postFetcher(`/add/${model}`, payload), {
    onSuccess: () => {
      message.success(_t('Succesfully added'));
      refetch();
      onCloseAdd();
    },
    onError: (error: Error) => {
      handleError(error, formAdd);
    },
  });

  const {
    mutate: mutateChange,
    isLoading: isLoadingChange,
    isError: isErrorChange,
  } = useMutation((payload: any) => patchFetcher(`/change/${model}/${openChange?.id}`, payload), {
    onSuccess: () => {
      message.success(_t('Succesfully changed'));
      refetch();
      onCloseChange();
    },
    onError: (error: Error) => {
      handleError(error, formChange);
    },
  });

  const { mutate: mutateDelete } = useMutation(
    (id: string) => deleteFetcher(`/delete/${model}/${id}`),
    {
      onSuccess: () => {
        resetTable(modelConfiguration?.preserve_filters);
        refetch();
        message.success(_t('Successfully deleted'));
      },
      onError: (error) => {
        handleError(error);
      },
    }
  );

  const { mutate: mutateAction, isLoading: isLoadingAction } = useMutation(
    (payload: any) => postFetcher(`/action/${model}/${action}`, payload),
    {
      onSuccess: () => {
        resetTable(modelConfiguration?.preserve_filters);
        refetch();
        message.success(_t('Successfully applied'));
      },
      onError: () => {
        message.error(_t('Server error'));
      },
    }
  );

  const onSelectRow = (v: string[]) => setSelectedRowKeys(v);
  const onApplyAction = useCallback(
    () => mutateAction({ ids: selectedRowKeys }),
    [mutateAction, selectedRowKeys]
  );

  const dateTimeFormat = configuration?.datetime_format;
  const columns = useTableColumns(
    modelConfiguration,
    dateTimeFormat,
    useCallback(
      (fieldName: string) => {
        return filters[fieldName];
      },
      [filters]
    ),
    useCallback(
      (fieldName: string, value: any) => {
        // onApplyFilter
        filters[fieldName] = value;
        setFilters({ ...filters });
        setPage(defaultPage);
        setPageSize(defaultPageSize);
      },
      [defaultPage, defaultPageSize, filters, setFilters, setPage, setPageSize]
    ),
    useCallback(
      (fieldName: string) => {
        // onRemoveFilter
        delete filters[fieldName];
        setFilters({ ...filters });
        setPage(defaultPage);
        setPageSize(defaultPageSize);
      },
      [defaultPage, defaultPageSize, filters, setFilters, setPage, setPageSize]
    ),
    useCallback(
      (record: any) => {
        // onDeleteItem
        mutateDelete(record.id);
      },
      [mutateDelete]
    ),
    useCallback(
      (record: any) => {
        // onChangeItem
        onOpenChange(record);
      },
      [onOpenChange]
    )
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
        {(modelConfiguration?.actions || []).length > 0 && modelConfiguration?.actions_on_top && (
          <Col>
            <Select
              placeholder={_t('Select Action By') as string}
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
              {_t('Apply')}
            </Button>
          </Col>
        )}
        {(modelConfiguration?.search_fields || []).length > 0 && (
          <Col>
            <Input.Search
              placeholder={modelConfiguration?.search_help_text || (_t('Search By') as string)}
              allowClear={true}
              onSearch={setSearch}
              style={{ width: 200 }}
            />
          </Col>
        )}
        {modelConfiguration?.permissions?.includes(EModelPermission.Export) && (
          <Col>
            <ExportBtn model={model} search={search} filters={filters} sortBy={sortBy} />
          </Col>
        )}
        {modelConfiguration?.permissions?.includes(EModelPermission.Add) && (
          <Col>
            <Button onClick={onOpenAdd} style={{ marginRight: -10 }}>
              <PlusCircleOutlined /> {_t('Add')}
            </Button>
          </Col>
        )}
      </Row>
    ),
    [
      _t,
      model,
      modelConfiguration?.actions,
      modelConfiguration?.actions_on_top,
      modelConfiguration?.permissions,
      modelConfiguration?.search_fields,
      modelConfiguration?.search_help_text,
      selectedRowKeys.length,
      action,
      setAction,
      onApplyAction,
      isLoadingAction,
      search,
      setSearch,
      filters,
      sortBy,
      onOpenAdd,
    ]
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
                      placeholder={_t('Select Action By') as string}
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
                      {_t('Apply')}
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
        {_t('Change')}
      </Button>
      <Modal
        width="100%"
        open={openList}
        title={
          modelConfiguration.verbose_name_plural ||
          `${modelConfiguration.verbose_name || getTitleFromModelClass(modelConfiguration.name)}s`
        }
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
        title={`Add ${getTitleFromModelClass(modelConfiguration.name)}`}
        onCancel={onCloseAdd}
        footer={null}
      >
        <Divider />
        {modelConfiguration && modelConfiguration.permissions.includes(EModelPermission.Add) ? (
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
                  <Button loading={isLoadingAdd} htmlType="submit" type="primary">
                    <SaveOutlined /> {_t('Add')}
                  </Button>
                </Space>
              </Col>
            </Row>
          </FormContainer>
        ) : (
          <Empty description={_t('No permissions for model')} />
        )}
      </Modal>
      <Modal
        width={600}
        open={!!openChange}
        title={`Change ${getTitleFromModelClass(modelConfiguration.name)} ${openChange?.id}`}
        onCancel={onCloseChange}
        footer={null}
      >
        <Divider />
        {modelConfiguration && modelConfiguration.permissions.includes(EModelPermission.Change) ? (
          <FormContainer
            modelConfiguration={modelConfiguration}
            form={formChange}
            onFinish={onFinishChange}
            mode="inline-change"
            hasOperationError={isErrorChange}
          >
            <Row justify="end">
              <Col>
                <Space>
                  <Button loading={isLoadingChange} htmlType="submit" type="primary">
                    <SaveOutlined /> {_t('Save')}
                  </Button>
                </Space>
              </Col>
            </Row>
          </FormContainer>
        ) : (
          <Empty description={_t('No permissions for model')} />
        )}
      </Modal>
    </div>
  );
};
