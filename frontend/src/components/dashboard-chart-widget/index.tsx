import { Area, Bar, Column, Line, Pie } from "@ant-design/charts";
import { FilterOutlined, InfoCircleOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import {
  Button,
  Card,
  Col,
  Form,
  Input,
  Modal,
  Radio,
  Row,
  Space,
  Spin,
  Tooltip,
  theme,
} from "antd";
import type React from "react";
import { useCallback, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { postFetcher } from "@/fetchers/fetchers";
import { getTitleFromFieldName } from "@/helpers/title";
import { transformValueToServer } from "@/helpers/transform";
import { getWidgetCls } from "@/helpers/widgets";
import {
  EDashboardWidgetType,
  type IModelWidgetAction,
  type IWidgetActionChartProps,
  type IWidgetActionFilter,
  type IWidgetActionResponse,
} from "@/interfaces/configuration";

interface DashboardChartWidgetProps {
  modelName: string;
  widgetAction: IModelWidgetAction;
}

const { useToken } = theme;

export const DashboardChartWidget: React.FC<DashboardChartWidgetProps> = ({
  modelName,
  widgetAction,
}) => {
  const { t: _t } = useTranslation("DashboardWidget");
  const { token } = useToken();

  const [filtersForm] = Form.useForm();
  const [filtersState, setFiltersState] = useState<Record<string, any>>({});
  const [modalFiltersState, setModalFiltersState] = useState<
    Record<string, any>
  >({});
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);

  const filters = useMemo(
    () => widgetAction.widget_action_filters || [],
    [widgetAction.widget_action_filters],
  );

  const hasValue = useCallback((value: any) => {
    if (value === undefined || value === null) {
      return false;
    }
    if (typeof value === "string") {
      return value.trim().length > 0;
    }
    /* v8 ignore next */
    if (Array.isArray(value)) {
      /* v8 ignore next */
      return value.length > 0;
    }
    /* v8 ignore next */
    return true;
  }, []);

  const queryPayload = useMemo(
    () =>
      filters.reduce(
        (acc, filter: IWidgetActionFilter) => {
          const rawValue = filtersState[filter.field_name];
          if (!hasValue(rawValue)) {
            return acc;
          }
          acc.push({
            field_name: filter.field_name,
            widget_type: filter.widget_type,
            value: transformValueToServer(rawValue),
          });
          return acc;
        },
        [] as {
          field_name: string;
          widget_type: IWidgetActionFilter["widget_type"];
          value: any;
        }[],
      ),
    [filters, filtersState, hasValue],
  );

  const hasActiveFilters = useMemo(
    () => filters.some((filter) => hasValue(filtersState[filter.field_name])),
    [filters, filtersState, hasValue],
  );

  const { data, isLoading } = useQuery<IWidgetActionResponse>({
    queryKey: ["/widget-action", modelName, widgetAction.name, queryPayload],
    /* v8 ignore next -- covered via react-query integration */
    queryFn: () =>
      postFetcher(`/widget-action/${modelName}/${widgetAction.name}`, {
        query: queryPayload,
      }),
    refetchOnWindowFocus: false,
  });

  const getFilterWidget = useCallback(
    (filter: IWidgetActionFilter, value: any, onChange: any) => {
      const [Widget, widgetProps]: any = getWidgetCls(filter.widget_type, _t);

      const onChangeWidget = (widgetValue: any) => {
        switch (Widget) {
          case Input:
          case Input.TextArea:
          case Radio.Group:
            onChange(widgetValue.target.value);
            break;
          default:
            onChange(widgetValue);
            break;
        }
      };

      return (
        <Widget
          placeholder={getTitleFromFieldName(filter.field_name)}
          {...(widgetProps || {})}
          {...(filter.widget_props || {})}
          value={value}
          onChange={onChangeWidget}
        />
      );
    },
    [_t],
  );

  const chartData = data?.data || [];
  const chartProps = widgetAction.widget_action_props as
    | IWidgetActionChartProps
    | undefined;
  const chartSeriesProps = useMemo(() => {
    if (!chartProps?.series_field) {
      return { color: token.colorPrimary };
    }

    const baseSeriesProps = {
      seriesField: chartProps.series_field,
      colorField: chartProps.series_field,
    };

    if (!chartProps.series_color) {
      return baseSeriesProps;
    }

    if (Array.isArray(chartProps.series_color)) {
      return {
        ...baseSeriesProps,
        color: chartProps.series_color,
      };
    }

    /* v8 ignore start -- visualization callback path */
    const seriesColorMap = chartProps.series_color;
    const seriesField = chartProps.series_field;
    return {
      ...baseSeriesProps,
      color: (datum: Record<string, unknown>) => {
        const seriesValue = String(datum[seriesField] ?? "");
        return seriesColorMap[seriesValue] || token.colorPrimary;
      },
    };
    /* v8 ignore stop */
  }, [chartProps, token.colorPrimary]);

  const openFiltersModal = () => {
    setModalFiltersState(filtersState);
    filtersForm.setFieldsValue(filtersState);
    setIsFiltersOpen(true);
  };

  const handleResetFilters = () => {
    setModalFiltersState({});
    filtersForm.resetFields();
    setFiltersState({});
    setIsFiltersOpen(false);
  };

  const handleApplyFilters = () => {
    setFiltersState(modalFiltersState);
    setIsFiltersOpen(false);
  };

  const titleNode = (
    <Space size={6}>
      <span>{widgetAction.title}</span>
      {widgetAction.description && (
        <Tooltip title={widgetAction.description}>
          <InfoCircleOutlined style={{ color: token.colorTextSecondary }} />
        </Tooltip>
      )}
    </Space>
  );

  return (
    <>
      <Card
        title={
          <Row justify="space-between" align="middle">
            <Col>{titleNode}</Col>
            {filters.length > 0 && (
              <Col>
                <Button
                  icon={<FilterOutlined />}
                  onClick={openFiltersModal}
                  type={hasActiveFilters ? "primary" : "default"}
                  danger={hasActiveFilters}
                >
                  {_t("Filters")}
                </Button>
              </Col>
            )}
          </Row>
        }
        key={`${modelName}-${widgetAction.name}`}
      >
        {!isLoading &&
          chartProps &&
          widgetAction.widget_action_type ===
            EDashboardWidgetType.ChartLine && (
            <Line
              data={chartData}
              xField={chartProps.x_field}
              yField={chartProps.y_field}
              legend={{
                position: "top-left",
              }}
              {...chartSeriesProps}
              {...(widgetAction.widget_action_props || {})}
            />
          )}
        {!isLoading &&
          chartProps &&
          widgetAction.widget_action_type ===
            EDashboardWidgetType.ChartArea && (
            <Area
              data={chartData}
              xField={chartProps.x_field}
              yField={chartProps.y_field}
              legend={{
                position: "top-left",
              }}
              {...chartSeriesProps}
              {...(widgetAction.widget_action_props || {})}
            />
          )}
        {!isLoading &&
          chartProps &&
          widgetAction.widget_action_type ===
            EDashboardWidgetType.ChartColumn && (
            <Column
              data={chartData}
              xField={chartProps.x_field}
              yField={chartProps.y_field}
              legend={{
                position: "top-left",
              }}
              {...chartSeriesProps}
              {...(widgetAction.widget_action_props || {})}
            />
          )}
        {!isLoading &&
          chartProps &&
          widgetAction.widget_action_type === EDashboardWidgetType.ChartBar && (
            <Bar
              data={chartData}
              xField={chartProps.x_field}
              yField={chartProps.y_field}
              legend={{
                position: "top-left",
              }}
              {...chartSeriesProps}
              {...(widgetAction.widget_action_props || {})}
            />
          )}
        {!isLoading &&
          chartProps &&
          widgetAction.widget_action_type === EDashboardWidgetType.ChartPie && (
            <Pie
              data={chartData}
              colorField={chartProps.series_field || chartProps.x_field}
              angleField={chartProps.y_field}
              legend={{
                position: "top-left",
              }}
              {...(widgetAction.widget_action_props || {})}
            />
          )}
        {isLoading && (
          <Row justify="center" align="middle">
            <Col>
              <Spin />
            </Col>
          </Row>
        )}
      </Card>

      {filters.length > 0 && (
        <Modal
          title={_t("Filters")}
          open={isFiltersOpen}
          /* v8 ignore next -- antd modal close internals */
          onCancel={() => setIsFiltersOpen(false)}
          footer={
            <Space>
              <Button onClick={handleResetFilters}>{_t("Reset")}</Button>
              <Button type="primary" onClick={handleApplyFilters}>
                {_t("Apply")}
              </Button>
            </Space>
          }
          destroyOnClose={true}
        >
          <Form form={filtersForm} layout="vertical">
            {filters.map((filter) => (
              <Form.Item
                key={filter.field_name}
                label={getTitleFromFieldName(filter.field_name)}
              >
                {getFilterWidget(
                  filter,
                  modalFiltersState[filter.field_name],
                  (nextValue: any) =>
                    setModalFiltersState((prev) => ({
                      ...prev,
                      [filter.field_name]: nextValue,
                    })),
                )}
              </Form.Item>
            ))}
          </Form>
        </Modal>
      )}
    </>
  );
};
