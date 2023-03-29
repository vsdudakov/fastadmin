import React, { useCallback } from 'react';
import querystring from 'querystring';
import { Bar } from '@ant-design/charts';
import { Card, Col, Row, Space, Spin } from 'antd';
import { SwapOutlined } from '@ant-design/icons';

import { EDashboardWidgetType, IDashboardWidget } from 'interfaces/configuration';
import { useQuery } from '@tanstack/react-query';
import { getFetcher } from 'fetchers/fetchers';
import { getWidgetCls } from 'helpers/widgets';
import { useTranslation } from 'react-i18next';

interface IDashboardWidgetProps {
  widget: IDashboardWidget;
}

export const DashboardWidget: React.FC<IDashboardWidgetProps> = ({ widget }) => {
  const { t: _t } = useTranslation('DashboardWidget');
  const [min, setMin] = React.useState<string | undefined>();
  const [max, setMax] = React.useState<string | undefined>();

  const queryString = querystring.stringify({
    min,
    max,
  });

  const { data, isLoading } = useQuery(
    [`/dashboard-widget/${widget.key}`, queryString],
    () => getFetcher(`/dashboard-widget/${widget.key}?${queryString}`),
    {
      refetchOnWindowFocus: false,
    }
  );

  const getFilterWidget = useCallback(
    (dashboardWidget: IDashboardWidget, placeholder: string, onChange: any) => {
      if (!dashboardWidget.x_field_filter_widget_type) {
        return null;
      }
      const [Widget, widgetProps]: any = getWidgetCls(
        dashboardWidget.x_field_filter_widget_type,
        _t
      );
      return (
        <Widget
          size="small"
          placeholder={placeholder}
          {...(widgetProps || {})}
          {...(dashboardWidget.x_field_filter_widget_props || {})}
          onChange={onChange}
        />
      );
    },
    [_t]
  );

  return (
    <Card
      title={
        <Row justify="space-between" style={{ lineHeight: 2 }}>
          <Col>{widget.title}</Col>
          {widget.x_field_filter_widget_type && (
            <Col>
              <Space>
                {getFilterWidget(widget, _t('From'), setMin)}
                <SwapOutlined />
                {getFilterWidget(widget, _t('To'), setMax)}
              </Space>
            </Col>
          )}
        </Row>
      }
      key={widget.title}
    >
      {!isLoading && widget.dashboard_widget_type === EDashboardWidgetType.ChartBar && (
        <Bar
          data={data?.results || []}
          xField={widget.x_field}
          yField={widget.y_field as string}
          seriesField={widget.series_field}
          legend={{
            position: 'top-left',
          }}
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
