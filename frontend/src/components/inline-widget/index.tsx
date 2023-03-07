import React, { useCallback, useContext, useState } from 'react';
import { Button, Col, Divider, Input, message, Modal, Row, Select, Tooltip } from 'antd';
import { DownloadOutlined, PlusCircleOutlined } from '@ant-design/icons';
import { useTranslation } from 'react-i18next';
import querystring from 'querystring';
import { useMutation, useQuery } from '@tanstack/react-query';
import fileDownload from 'react-file-download';
import { v4 as uuidv4 } from 'uuid';

import { TableOrCards } from 'components/table-or-cards';
import { useTableQuery } from 'hooks/useTableQuery';
import { ADD_PK_PREFIX, useTableColumns } from 'hooks/useTableColumns';
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

  const [open, setOpen] = useState<boolean>(false);
  const [updatedRows, setUpdatedRows] = useState<Record<string, any>[]>([]);

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
      refetchOnWindowFocus: false,
      onSuccess: () => {
        setUpdatedRows([]);
      },
    }
  );

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
        resetTable(modelConfiguration?.preserve_filters);
        refetch();
        message.success(_t('Successfully applied'));
      },
      onError: () => {
        message.error(_t('Server error'));
      },
    }
  );

  const { mutate: mutateSaveInline, isLoading: isLoadingSaveInline } = useMutation(
    (payload: any) => postFetcher(`/save-inline/${model}`, payload),
    {
      onSuccess: () => {
        resetTable();
        setUpdatedRows([]);
        setOpen(false);
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
      (record: any) => {
        // onDeleteItem
        mutateDelete(record.id);
      },
      [mutateDelete]
    ),
    useCallback(
      (record: any) => {
        // onChangeItem
        if (!updatedRows.find((i) => i.id === record.id)) {
          setUpdatedRows([...updatedRows, record]);
        } else {
          setUpdatedRows(updatedRows.filter((i) => i.id !== record.id));
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
    resetTable();
    setUpdatedRows([]);
    setOpen(false);
  };

  const onSave = () => {
    const payload: any = [];
    updatedRows.forEach((r) => {
      const row = { ...r, id: undefined };
      payload.push(row);
    });
    mutateSaveInline(payload);
  };

  const onAdd = useCallback(() => {
    setUpdatedRows([...updatedRows, { id: `${ADD_PK_PREFIX}${uuidv4()}` }]);
  }, [updatedRows]);

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
              <Tooltip title={_t('Add a line')}>
                <Button type="dashed" onClick={onAdd}>
                  <PlusCircleOutlined /> {_t('Add')}
                </Button>
              </Tooltip>
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
    onAdd,
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
              dataSource={[
                ...(data?.results || []),
                ...updatedRows.filter((i) => String(i.id).startsWith(ADD_PK_PREFIX)),
              ]}
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
        <Row justify="end">
          <Col>
            <Button type="primary" loading={isLoadingSaveInline} onClick={onSave}>
              {_t('Save')}
            </Button>
          </Col>
        </Row>
      </Modal>
    </div>
  );
};
