import React, { useContext, useMemo, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Breadcrumb, Button, Empty, message, Popconfirm, Space, Table } from 'antd';
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
import { EFieldWidgetType, EModelPermission, IModel, IModelField } from 'interfaces/configuration';
import { getTitleFromFieldName } from 'helpers/title';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { deleteFetcher, getFetcher, postFetcher } from 'fetchers/fetchers';
import { FilterColumn } from './filter-column';
import { transformFilters } from 'helpers/filters';

const DEFAULT_PAGE = 1;
const DEFAULT_PAGE_SIZE = 10;

export const List: React.FC = () => {
  const { configuration } = useContext(ConfigurationContext);
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { t: _t } = useTranslation('List');
  const { model } = useParams();

  const [filters, setFilters] = useState<any>({});
  const [page, setPage] = useState<number>(DEFAULT_PAGE);
  const [pageSize, setPageSize] = useState<number>(DEFAULT_PAGE_SIZE);
  const [sortBy, setSortBy] = useState<string | undefined>();

  const modelConfiguration: IModel | undefined = configuration.models.find(
    (item: IModel) => item.name === model
  );

  const columns = useMemo(() => {
    return (modelConfiguration || { fields: [] }).fields.map((field: IModelField) => {
      return {
        title: getTitleFromFieldName(field.name),
        dataIndex: field.name,
        key: field.name,
        sorter: field.list_configuration?.sorter,
        filterIcon: !!field?.list_configuration?.widget_type ? (
          !!filters[field.name] ? (
            <FilterFilled />
          ) : (
            <FilterOutlined />
          )
        ) : undefined,
        filterDropdown: !!field?.list_configuration?.widget_type
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
                  widgetType={field?.list_configuration?.widget_type as EFieldWidgetType}
                  widgetProps={field?.list_configuration?.widget_props}
                  value={filters[field.name]}
                  onFilter={onFilter}
                  onReset={onReset}
                />
              );
            }
          : undefined,
      };
    });
  }, [modelConfiguration, filters]);

  const queryString = querystring.stringify({
    sort_by: sortBy,
    offset: (page - 1) * pageSize,
    limit: pageSize,
    ...transformFilters(filters),
  });

  const { data, isLoading } = useQuery([`/list/${model}`, queryString], () =>
    getFetcher(`/list/${model}?${queryString}`)
  );

  const { mutate: mutateExport, isLoading: isLoadingExport } = useMutation(
    () => postFetcher(`/export/${model}`, {}),
    {
      onSuccess: (data) => {
        fileDownload(data, `${model}.csv`);
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
        queryClient.invalidateQueries([`/list/${model}`]);
        setPage(DEFAULT_PAGE);
        setPageSize(DEFAULT_PAGE_SIZE);
        setFilters({});
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
      actions={
        <Space>
          {modelConfiguration?.permissions?.includes(EModelPermission.Export) && (
            <Button loading={isLoadingExport} onClick={() => mutateExport()}>
              <DownloadOutlined /> {_t('Export CSV')}
            </Button>
          )}
          {modelConfiguration?.permissions?.includes(EModelPermission.Add) && (
            <Button onClick={() => navigate(`/add/${model}`)}>
              <PlusCircleOutlined /> {_t('Add')}
            </Button>
          )}
        </Space>
      }
    >
      {modelConfiguration ? (
        <Table
          loading={isLoading}
          columns={[
            ...columns,
            {
              title: _t('Actions'),
              dataIndex: 'id',
              key: 'actions',
              width: 100,
              fixed: 'right',
              render: (id: string) => {
                return (
                  <Space>
                    {modelConfiguration.permissions.includes(EModelPermission.Delete) && (
                      <Popconfirm title={_t('Are you sure?')} onConfirm={() => mutateDelete(id)}>
                        <Button size="small" danger>
                          <DeleteOutlined />
                        </Button>
                      </Popconfirm>
                    )}
                    {modelConfiguration.permissions.includes(EModelPermission.Change) && (
                      <Button size="small" onClick={() => navigate(`/change/${model}/${id}`)}>
                        <EditOutlined />
                      </Button>
                    )}
                  </Space>
                );
              },
            },
          ]}
          onChange={onTableChange}
          rowKey={'id'}
          dataSource={data?.results || []}
          pagination={{
            current: page,
            pageSize,
            total: data?.total,
            showSizeChanger: true,
          }}
        />
      ) : (
        <Empty description={_t('No permissions for model')} />
      )}
    </CrudContainer>
  );
};
