import { Button, Popconfirm, Space, Tooltip } from 'antd';
import { getTitleFromFieldName } from 'helpers/title';
import {
  EFieldWidgetType,
  EModelPermission,
  IAddConfigurationField,
  IChangeConfigurationField,
  IModel,
  IModelField,
} from 'interfaces/configuration';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import {
  FilterOutlined,
  FilterFilled,
  DeleteOutlined,
  EditOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import { FilterColumn } from 'components/filter-column';
import { transformColumnValueFromServer, transformValueFromServer } from 'helpers/transform';
import { getWidgetCls } from 'helpers/widgets';

export const useTableColumns = (
  modelConfiguration: IModel | undefined,
  dateTimeFormat: string | undefined,
  getFilterValue: any,
  onApplyFilter: any,
  onResetFilter: any,
  onDeleteItem: any,
  onChangeItem: any,
  updatedRows: Record<string, Record<string, any>>
): any => {
  const { t: _t } = useTranslation('List');
  const fields = (modelConfiguration || { fields: [] }).fields;

  const getWidget = useCallback(
    (configurationField: IAddConfigurationField | IChangeConfigurationField, value: any) => {
      if (!configurationField.form_widget_type) {
        return null;
      }
      const [Widget, widgetProps]: any = getWidgetCls(configurationField.form_widget_type, _t);
      return (
        <Widget
          defaultValue={value}
          {...(widgetProps || {})}
          {...(configurationField.form_widget_props || {})}
        />
      );
    },
    [_t]
  );

  return useMemo(() => {
    const columns = fields
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
            !!getFilterValue(field.name) ? (
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
                  onResetFilter(field.name);
                  clearFilters();
                  confirm();
                };
                const onApply = (value: any) => {
                  onApplyFilter(field.name, value);
                  confirm();
                };
                return (
                  <FilterColumn
                    widgetType={field.list_configuration?.filter_widget_type as EFieldWidgetType}
                    widgetProps={field.list_configuration?.filter_widget_props}
                    value={getFilterValue(field.name)}
                    onFilter={onApply}
                    onReset={onReset}
                  />
                );
              }
            : undefined,
          render: (value: any, record: any) => {
            if (updatedRows[record.id] && field.change_configuration?.form_widget_type) {
              const fieldValue = transformValueFromServer(value);
              return getWidget(field.change_configuration, fieldValue);
            }

            if (value === undefined) {
              return field.list_configuration?.empty_value_display;
            }
            const transformedValue = transformColumnValueFromServer(
              value,
              field.list_configuration?.empty_value_display,
              dateTimeFormat
            );
            if (field?.list_configuration?.is_link) {
              const onChange = () => onChangeItem(record.id);
              return <span onClick={onChange}>{transformedValue}</span>;
            }

            return transformedValue;
          },
        };
      });
    columns.push({
      title: _t('Actions'),
      dataIndex: 'id',
      key: 'actions',
      width: 100,
      fixed: 'right',
      render: (id: string) => {
        const onDelete = () => onDeleteItem(id);
        const onChange = () => onChangeItem(id);
        return (
          <Space>
            {(modelConfiguration?.permissions || []).includes(EModelPermission.Delete) && (
              <Popconfirm title={_t('Are you sure?')} onConfirm={onDelete}>
                <Button size="small" danger={true}>
                  <DeleteOutlined />
                </Button>
              </Popconfirm>
            )}
            {(modelConfiguration?.permissions || []).includes(EModelPermission.Change) && (
              <Button danger={!!updatedRows[id]} size="small" onClick={onChange}>
                {!updatedRows[id] ? (
                  <EditOutlined />
                ) : (
                  <Tooltip title={_t('Reset changes')}>
                    <CloseCircleOutlined />
                  </Tooltip>
                )}
              </Button>
            )}
          </Space>
        );
      },
    } as any);
    return columns;
  }, [
    _t,
    dateTimeFormat,
    fields,
    getFilterValue,
    getWidget,
    modelConfiguration?.permissions,
    onApplyFilter,
    onChangeItem,
    onDeleteItem,
    onResetFilter,
    updatedRows,
  ]);
};
