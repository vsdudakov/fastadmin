import React, { useContext, useEffect, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Breadcrumb,
  Button,
  Col,
  Empty,
  Input,
  message,
  Popconfirm,
  Row,
  Space,
  Switch,
  Tooltip,
  Select,
} from 'antd';
import querystring from 'querystring';
import {
  DownloadOutlined,
  PlusCircleOutlined,
  EditOutlined,
  DeleteOutlined,
  FilterOutlined,
  FilterFilled,
} from '@ant-design/icons';
import fileDownload from 'react-file-download';

import { CrudContainer } from 'components/crud-container';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import {
  EFieldWidgetType,
  EModelPermission,
  IModel,
  IModelAction,
  IModelField,
} from 'interfaces/configuration';
import { getTitleFromFieldName } from 'helpers/title';
import { useMutation, useQuery } from '@tanstack/react-query';
import { deleteFetcher, getFetcher, postFetcher } from 'fetchers/fetchers';
import { FilterColumn } from './filter-column';
import { transformColumnValueFromServer, transformFiltersToServer } from 'helpers/transform';
import { TableOrCards } from 'components/table-or-cards';
import { handleError } from 'helpers/forms';
import { useIsMobile } from 'hooks/useIsMobile';

const DEFAULT_PAGE = 1;
const DEFAULT_PAGE_SIZE = 10;

export const List: React.FC = () => {
  const { configuration } = useContext(ConfigurationContext);
  const navigate = useNavigate();
  const { t: _t } = useTranslation('List');
  const { model } = useParams();
  const isMobile = useIsMobile();

  const [action, setAction] = useState<string | undefined>();
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([]);

  const [filters, setFilters] = useState<any>({});
  const [search, setSearch] = useState<string | undefined>();
  const [page, setPage] = useState<number>(DEFAULT_PAGE);
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);
  const [sortBy, setSortBy] = useState<string | undefined>();

  const dateTimeFormat = configuration?.datetime_format;
  const modelConfiguration: IModel | undefined = configuration.models.find(
    (item: IModel) => item.name === model
  );

  useEffect(() => {
    if (modelConfiguration?.list_per_page) {
      setPageSize(modelConfiguration?.list_per_page);
    }
  }, [modelConfiguration?.list_per_page]);

  useEffect(() => {
    if (model) {
      setPage(DEFAULT_PAGE);
      setSortBy(undefined);
    }
  }, [model]);

  const fields = (modelConfiguration || { fields: [] }).fields;
  const columns = useMemo(() => {
    return fields
      .filter((field: IModelField) => !!field.list_configuration)
      .sort(
        (a: IModelField, b: IModelField) =>
          (a.list_configuration?.index || 0) - (b.list_configuration?.index || 0)
      )
      .map((field: IModelField) => {
        return {
          title: getTitleFromFieldName(field.name),
          dataIndex: field.name,
          key: field.name,
          sorter: field.list_configuration?.sorter,
          filterIcon: !!field.list_configuration?.filter_widget_type ? (
            filters[field.name] !== undefined ? (
              <Tooltip title={_t('Click to reset this filter')}>
                <FilterFilled style={{ color: 'red' }} />
              </Tooltip>
            ) : (
              <Tooltip title={_t('Click to filter')}>
                <FilterOutlined />
              </Tooltip>
            )
          ) : undefined,
          filterDropdown: !!field.list_configuration?.filter_widget_type
            ? ({ confirm, clearFilters }: any) => {
                const onReset = () => {
                  delete filters[field.name];
                  setFilters({ ...filters });
                  setPage(DEFAULT_PAGE);
                  setPageSize(DEFAULT_PAGE_SIZE);
                  clearFilters();
                  confirm();
                };
                const onFilter = (value: any) => {
                  filters[field.name] = value;
                  setFilters({ ...filters });
                  setPage(DEFAULT_PAGE);
                  setPageSize(DEFAULT_PAGE_SIZE);
                  confirm();
                };
                return (
                  <FilterColumn
                    widgetType={field.list_configuration?.filter_widget_type as EFieldWidgetType}
                    widgetProps={field.list_configuration?.filter_widget_props}
                    value={filters[field.name]}
                    onFilter={onFilter}
                    onReset={onReset}
                  />
                );
              }
            : undefined,
          render: (value: any, record: any) => {
            if (value === undefined) {
              return field.list_configuration?.empty_value_display;
            }
            const transformedValue = transformColumnValueFromServer(
              value,
              field.list_configuration?.empty_value_display,
              dateTimeFormat,
              (v: boolean) => <Switch checked={v} size="small" />
            );
            if (field?.list_configuration?.is_link) {
              return <Link to={`/change/${model}/${record.id}`}>{transformedValue}</Link>;
            }
            return transformedValue;
          },
        };
      });
  }, [model, fields, filters, dateTimeFormat, _t]);

  const queryString = querystring.stringify({
    search,
    sort_by: sortBy,
    offset: (page - 1) * pageSize,
    limit: pageSize,
    ...transformFiltersToServer(filters),
  });

  const { data, isLoading, refetch } = useQuery([`/list/${model}`, queryString], () =>
    getFetcher(`/list/${model}?${queryString}`)
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

  const { mutate: mutateDelete } = useMutation(
    (id: string) => deleteFetcher(`/delete/${model}/${id}`),
    {
      onSuccess: () => {
        message.success(_t('Successfully deleted'));
        refetch();
        setPage(DEFAULT_PAGE);
        setPageSize(DEFAULT_PAGE_SIZE);
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

  const { mutate: mutateAction, isLoading: isLoadingAction } = useMutation(
    (payload: any) => postFetcher(`/action/${model}/${action}`, payload),
    {
      onSuccess: () => {
        refetch();
        setSelectedRowKeys([]);
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

  const onTableChange = (pagination: any, tableFilters: any, sorter: any): void => {
    if (pagination.pageSize !== pageSize) {
      setPage(1);
    } else {
      setPage(pagination.current);
    }
    setPageSize(pagination.pageSize);
    setSortBy(sorter.order === 'ascend' ? sorter.field : `-${sorter.field}`);
  };

  const onExport = () => mutateExport();
  const onAdd = () => navigate(`/add/${model}`);

  const onSelectRow = (v: string[]) => setSelectedRowKeys(v);
  const onApplyAction = () => mutateAction({ ids: selectedRowKeys });

  return (
    <CrudContainer
      title={modelConfiguration?.name || model || ''}
      breadcrumbs={
        <Breadcrumb>
          <Breadcrumb.Item>
            <Link to="/">{_t('Dashboard')}</Link>
          </Breadcrumb.Item>
          <Breadcrumb.Item>{model}</Breadcrumb.Item>
        </Breadcrumb>
      }
      viewOnSite={modelConfiguration?.view_on_site}
      headerActions={
        <Row style={{ marginTop: 10, marginBottom: 10 }} gutter={[8, 8]}>
          {(modelConfiguration?.actions || []).length > 0 && modelConfiguration?.actions_on_top && (
            <Col>
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
              <Button loading={isLoadingExport} onClick={onExport}>
                <DownloadOutlined /> {_t('Export CSV')}
              </Button>
            </Col>
          )}
          {modelConfiguration?.permissions?.includes(EModelPermission.Add) && (
            <Col>
              <Button onClick={onAdd}>
                <PlusCircleOutlined /> {_t('Add')}
              </Button>
            </Col>
          )}
        </Row>
      }
      bottomActions={
        <>
          {(modelConfiguration?.actions || []).length > 0 &&
            modelConfiguration?.actions_on_bottom && (
              <div style={{ marginTop: isMobile ? 10 : -50 }}>
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
        </>
      }
    >
      {modelConfiguration ? (
        <TableOrCards
          loading={isLoading}
          rowSelection={{
            selectedRowKeys,
            onChange: onSelectRow as any,
          }}
          sticky={true}
          columns={[
            ...columns,
            {
              title: _t('Actions'),
              dataIndex: 'id',
              key: 'actions',
              width: 100,
              fixed: 'right',
              render: (id: string) => {
                const onDelete = () => mutateDelete(id);
                const onChange = () => navigate(`/change/${model}/${id}`);
                return (
                  <Space>
                    {modelConfiguration.permissions.includes(EModelPermission.Delete) && (
                      <Popconfirm title={_t('Are you sure?')} onConfirm={onDelete}>
                        <Button size="small" danger={true}>
                          <DeleteOutlined />
                        </Button>
                      </Popconfirm>
                    )}
                    {modelConfiguration.permissions.includes(EModelPermission.Change) && (
                      <Button size="small" onClick={onChange}>
                        <EditOutlined />
                      </Button>
                    )}
                  </Space>
                );
              },
            },
          ]}
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
      ) : (
        <Empty description={_t('No permissions for model')} />
      )}
    </CrudContainer>
  );
};
