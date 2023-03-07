import React, { useCallback, useContext, useState } from 'react';
import { Button, Col, Divider, Form, Input, message, Modal, Row, Select } from 'antd';
import { DownloadOutlined, PlusCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import querystring from 'querystring';
import { useMutation, useQuery } from '@tanstack/react-query';
import fileDownload from 'react-file-download';

import { TableOrCards } from 'components/table-or-cards';
import { useTableQuery } from 'hooks/useTableQuery';
import { useTableColumns } from 'hooks/useTableColumns';
import { handleError } from 'helpers/forms';
import { transformFiltersToServer } from 'helpers/transform';
import { deleteFetcher, getFetcher, postFetcher } from 'fetchers/fetchers';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { EModelPermission, IInlineModel, IModelAction } from 'interfaces/configuration';

export interface IInlineWidget {
  modelConfiguration: IInlineModel;
}

export const InlineWidget: React.FC<IInlineWidget> = ({ modelConfiguration }) => {
  const { t: _t } = useTranslation('Inline');
  const { configuration } = useContext(ConfigurationContext);

  const [form] = Form.useForm();
  const [open, setOpen] = useState<boolean>(false);
  const [updatedRows, setUpdatedRows] = useState<Record<string, Record<string, any>>>({});

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
  } = useTableQuery(modelConfiguration);

  const model = modelConfiguration.name;

  const queryString = querystring.stringify({
    search,
    sort_by: sortBy,
    offset: (page - 1) * pageSize,
    limit: pageSize,
    ...transformFiltersToServer(filters),
  });

  const { data, isLoading, refetch } = useQuery(
    [`/list/${model}`, queryString],
    () => getFetcher(`/list/${model}?${queryString}`),
    {
      enabled: open,
      onSuccess: () => {
        setUpdatedRows({});
      },
    }
  );

  const { mutate: mutateDelete } = useMutation(
    (id: string) => deleteFetcher(`/delete/${model}/${id}`),
    {
      onSuccess: () => {
        message.success(_t('Successfully deleted'));
        refetch();
        setPage(defaultPage);
        setPageSize(defaultPageSize);
        if (!modelConfiguration?.preserve_filters) {
          setFilters({});
          setSearch(undefined);
        }
      },
      onError: (error) => {
        handleError(error);
      },
    }
  );

  const exportQueryString = querystring.stringify({
    search,
    sort_by: sortBy,
    ...transformFiltersToServer(filters),
  });

  const { mutate: mutateExport, isLoading: isLoadingExport } = useMutation(
    () =>
      postFetcher(`/export/${model}?${exportQueryString}`, {
        format: 'CSV',
        offset: 0,
        limit: 1000,
      }),
    {
      onSuccess: (d) => {
        fileDownload(d, `${model}.csv`);
        message.success(_t('Successfully exported'));
      },
      onError: () => {
        message.error(_t('Server error'));
      },
    }
  );

  const { mutate: mutateAction, isLoading: isLoadingAction } = useMutation(
    (payload: any) => postFetcher(`/action/${model}/${action}`, payload),
    {
      onSuccess: () => {
        refetch();
        setSelectedRowKeys([]);
        setAction(undefined);
        message.success(_t('Successfully applied'));
        if (!modelConfiguration?.preserve_filters) {
          setFilters({});
          setSearch(undefined);
        }
      },
      onError: () => {
        message.error(_t('Server error'));
      },
    }
  );

  const onSelectRow = (v: string[]) => setSelectedRowKeys(v);
  const onExport = useCallback(() => mutateExport(), [mutateExport]);
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
      (id: string) => {
        // onDeleteItem
        mutateDelete(id);
      },
      [mutateDelete]
    ),
    useCallback(
      (id: string) => {
        // onChangeItem
        if (!updatedRows[id]) {
          setUpdatedRows({ ...updatedRows, [id]: {} });
        } else {
          delete updatedRows[id];
          setUpdatedRows({ ...updatedRows });
        }
      },
      [updatedRows]
    ),
    updatedRows
  );

  const onOpen = () => {
    setOpen(true);
  };

  const onClose = () => {
    setOpen(false);
  };

  const onReset = () => {
    form.resetFields();
    setOpen(false);
  };

  const onSave = () => {
    form.submit();
    setOpen(false);
  };

  const tableHeader = useCallback(
    () => (
      <Row justify="end">
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
            <Button
              style={{ marginRight: -10, marginLeft: 5 }}
              loading={isLoadingExport}
              onClick={onExport}
            >
              <DownloadOutlined /> {_t('Export CSV')}
            </Button>
          </Col>
        )}
      </Row>
    ),
    [
      _t,
      action,
      isLoadingAction,
      isLoadingExport,
      modelConfiguration?.actions,
      modelConfiguration?.actions_on_top,
      modelConfiguration?.permissions,
      modelConfiguration?.search_fields,
      modelConfiguration?.search_help_text,
      onApplyAction,
      onExport,
      selectedRowKeys.length,
      setAction,
      setSearch,
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
            <Col>
              <Button type="dashed">
                <PlusCircleOutlined /> {_t('Add')}
              </Button>
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

  const getRowClass = (row: any) =>
    !!updatedRows[row.id] ? 'table-row-selected' : (undefined as any);

  return (
    <div>
      <Button style={{ minWidth: 200 }} type="dashed" onClick={onOpen}>
        {_t('Change')}
      </Button>
      <Modal
        width="100%"
        open={open}
        title={
          modelConfiguration.verbose_name_plural ||
          `${modelConfiguration.verbose_name || modelConfiguration.name}s`
        }
        onCancel={onClose}
        footer={null}
      >
        <Row>
          <Col xs={24}>
            <TableOrCards
              rowClassName={getRowClass}
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
        <Divider />
        <Row justify="space-between">
          <Col>
            <Button onClick={onReset}>{_t('Reset')}</Button>
          </Col>
          <Col>
            <Button type="primary" onClick={onSave}>
              {_t('Save')}
            </Button>
          </Col>
        </Row>
      </Modal>
    </div>
  );
};
