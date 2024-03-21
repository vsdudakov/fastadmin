import {
  DeleteOutlined,
  EditOutlined,
  FilterFilled,
  FilterOutlined,
} from "@ant-design/icons";
import { Button, Popconfirm, Space, Tooltip } from "antd";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

import { FilterColumn } from "@/components/filter-column";
import { getTitleFromFieldName } from "@/helpers/title";
import { isString, transformColumnValueFromServer } from "@/helpers/transform";
import {
  type EFieldWidgetType,
  EModelPermission,
  type IModel,
  type IModelField,
} from "@/interfaces/configuration";

export const useTableColumns = (
  modelConfiguration: IModel | undefined,
  dateTimeFormat: string | undefined,

  getFilterValue: any,

  onApplyFilter: any,

  onResetFilter: any,

  onDeleteItem: any,

  onChangeItem: any,
): any => {
  const { t: _t } = useTranslation("List");
  const fields = (modelConfiguration || { fields: [] }).fields;

  return useMemo(() => {
    const columns = fields
      .filter((field: IModelField) => !!field.list_configuration)
      .sort(
        (a: IModelField, b: IModelField) =>
          (a.list_configuration?.index || 0) -
          (b.list_configuration?.index || 0),
      )
      .map((field: IModelField) => {
        return {
          title: getTitleFromFieldName(field.name),
          dataIndex: field.name,
          key: field.name,
          sorter: field.list_configuration?.sorter,
          width: field.list_configuration?.width,
          ellipsis: true,
          filterIcon: field.list_configuration?.filter_widget_type ? (
            getFilterValue(field.name) ? (
              <Tooltip title={_t("Click to reset this filter")}>
                <FilterFilled style={{ color: "red" }} />
              </Tooltip>
            ) : (
              <Tooltip title={_t("Click to filter")}>
                <FilterOutlined />
              </Tooltip>
            )
          ) : undefined,
          filterDropdown: field.list_configuration?.filter_widget_type
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
                    widgetType={
                      field.list_configuration
                        ?.filter_widget_type as EFieldWidgetType
                    }
                    widgetProps={field.list_configuration?.filter_widget_props}
                    value={getFilterValue(field.name)}
                    onFilter={onApply}
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
            );
            if (field?.list_configuration?.is_link) {
              const onChange = () => onChangeItem(record);
              return (
                <Button style={{ padding: 0 }} type="link" onClick={onChange}>
                  {transformedValue}
                </Button>
              );
            }
            if (
              isString(transformedValue) &&
              (transformedValue.startsWith("http") ||
                transformedValue.startsWith("/"))
            ) {
              return (
                <a href={transformedValue} target="_blank" rel="noreferrer">
                  {transformedValue}
                </a>
              );
            }

            return transformedValue;
          },
        };
      });
    columns.push({
      title: _t("Actions"),
      key: "actions",
      width: 100,
      fixed: "right",

      render: (record: any) => {
        const onDelete = () => onDeleteItem(record);
        const onChange = () => onChangeItem(record);
        return (
          <Space>
            {(modelConfiguration?.permissions || []).includes(
              EModelPermission.Delete,
            ) && (
              <Popconfirm title={_t("Are you sure?")} onConfirm={onDelete}>
                <Button size="small" danger={true}>
                  <DeleteOutlined />
                </Button>
              </Popconfirm>
            )}
            {(modelConfiguration?.permissions || []).includes(
              EModelPermission.Change,
            ) && (
              <Button size="small" onClick={onChange}>
                <EditOutlined />
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
    modelConfiguration?.permissions,
    onApplyFilter,
    onChangeItem,
    onDeleteItem,
    onResetFilter,
  ]);
};
