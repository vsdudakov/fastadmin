import { Area, Bar, Column, Line, Pie } from "@ant-design/charts";
import { SwapOutlined } from "@ant-design/icons";
import { useQuery } from "@tanstack/react-query";
import { Card, Col, Input, Radio, Row, Select, Space, Spin, theme } from "antd";
import querystring from "query-string";
import React, { useCallback, useEffect } from "react";
import { useTranslation } from "react-i18next";

import { getFetcher } from "@/fetchers/fetchers";
import { getTitleFromFieldName } from "@/helpers/title";
import {
  transformValueFromServer,
  transformValueToServer,
} from "@/helpers/transform";
import { getWidgetCls } from "@/helpers/widgets";
import {
  EDashboardWidgetType,
  type IDashboardWidget,
} from "@/interfaces/configuration";

interface IDashboardWidgetProps {
  widget: IDashboardWidget;
}

const { useToken } = theme;

export const DashboardWidget: React.FC<IDashboardWidgetProps> = ({
  widget,
}) => {
  const { t: _t } = useTranslation("DashboardWidget");
  const { token } = useToken();

  const [min, setMin] = React.useState<any>();

  const [max, setMax] = React.useState<any>();

  const [period, setPeriod] = React.useState<any>();

  const queryString = querystring.stringify({
    min_x_field: transformValueToServer(min),
    max_x_field: transformValueToServer(max),
    period_x_field: transformValueToServer(period),
  });

  const { data, isLoading } = useQuery({
    queryKey: ["/dashboard-widget", widget.key, queryString],
    queryFn: () => getFetcher(`/dashboard-widget/${widget.key}?${queryString}`),
    refetchOnWindowFocus: false,
  });

  useEffect(() => {
    if (data) {
      setMin(transformValueFromServer(data.min_x_field));
      setMax(transformValueFromServer(data.max_x_field));
      setPeriod(transformValueFromServer(data.period_x_field));
    }
  }, [data]);

  const getFilterWidget = useCallback(
    (
      dashboardWidget: IDashboardWidget,
      placeholder: string,
      value: string | undefined,

      onChange: any,
    ) => {
      if (!dashboardWidget.x_field_filter_widget_type) {
        return null;
      }

      const [Widget, widgetProps]: any = getWidgetCls(
        dashboardWidget.x_field_filter_widget_type,
        _t,
      );

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
          size="small"
          placeholder={placeholder}
          {...(widgetProps || {})}
          {...(dashboardWidget.x_field_filter_widget_props || {})}
          value={value}
          onChange={onChangeWidget}
        />
      );
    },
    [_t],
  );

  return (
    <Card
      title={
        <Row justify="space-between" style={{ lineHeight: 2 }}>
          <Col>{widget.title}</Col>
          {widget.x_field_filter_widget_type && (
            <Col>
              <Space>
                {widget.x_field_periods && (
                  <Select
                    allowClear={true}
                    style={{ width: 100 }}
                    options={widget.x_field_periods.map((value: string) => ({
                      label: getTitleFromFieldName(value),
                      value,
                    }))}
                    value={period}
                    onChange={setPeriod}
                    size="small"
                  />
                )}
                {getFilterWidget(widget, _t("From"), min, setMin)}
                <SwapOutlined />
                {getFilterWidget(widget, _t("To"), max, setMax)}
              </Space>
            </Col>
          )}
        </Row>
      }
      key={widget.title}
    >
      {!isLoading &&
        widget.dashboard_widget_type === EDashboardWidgetType.ChartLine && (
          <Line
            data={data?.results || []}
            xField={widget.x_field}
            yField={widget.y_field}
            legend={{
              position: "top-left",
            }}
            colorField={token.colorPrimary}
            {...(widget.dashboard_widget_props || {})}
          />
        )}
      {!isLoading &&
        widget.dashboard_widget_type === EDashboardWidgetType.ChartArea && (
          <Area
            data={data?.results || []}
            xField={widget.x_field}
            yField={widget.y_field}
            legend={{
              position: "top-left",
            }}
            colorField={token.colorPrimary}
            {...(widget.dashboard_widget_props || {})}
          />
        )}
      {!isLoading &&
        widget.dashboard_widget_type === EDashboardWidgetType.ChartColumn && (
          <Column
            data={data?.results || []}
            xField={widget.x_field}
            yField={widget.y_field}
            legend={{
              position: "top-left",
            }}
            colorField={token.colorPrimary}
            {...(widget.dashboard_widget_props || {})}
          />
        )}
      {!isLoading &&
        widget.dashboard_widget_type === EDashboardWidgetType.ChartBar && (
          <Bar
            data={data?.results || []}
            xField={widget.x_field}
            yField={widget.y_field}
            legend={{
              position: "top-left",
            }}
            colorField={token.colorPrimary}
            {...(widget.dashboard_widget_props || {})}
          />
        )}
      {!isLoading &&
        widget.dashboard_widget_type === EDashboardWidgetType.ChartPie && (
          <Pie
            data={data?.results || []}
            colorField={widget.x_field}
            angleField={widget.y_field}
            legend={{
              position: "top-left",
            }}
            {...(widget.dashboard_widget_props || {})}
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
  );
};
