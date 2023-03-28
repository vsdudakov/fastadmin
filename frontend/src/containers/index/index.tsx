import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { Breadcrumb, Col, Collapse, Empty, Row } from 'antd';
import { Link } from 'react-router-dom';
import { Bar } from '@ant-design/plots';

import { CrudContainer } from 'components/crud-container';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { EDashboardWidgetType, IDashboardWidget } from 'interfaces/configuration';

export const Index: React.FC = () => {
  const { t: _t } = useTranslation('Dashboard');
  const { configuration } = useContext(ConfigurationContext);
  return (
    <CrudContainer
      title={_t('Dashboard')}
      breadcrumbs={
        <Breadcrumb>
          <Breadcrumb.Item>
            <Link to="/">{_t('Dashboard')}</Link>
          </Breadcrumb.Item>
        </Breadcrumb>
      }
    >
      <Row gutter={[16, 16]}>
        {configuration.dashboard_widgets.map((widget: IDashboardWidget) => (
          <Col xs={24} md={12} key={widget.title}>
            <Collapse defaultActiveKey={[widget.title]}>
              <Collapse.Panel header={widget.title} key={widget.title}>
                {widget.dashboard_widget_type === EDashboardWidgetType.ChartBar && (
                  <Bar
                    data={[]}
                    xField={widget.x_field}
                    yField={widget.y_field as string}
                    seriesField={widget.series_field}
                    legend={{
                      position: 'top-left',
                    }}
                  />
                )}
              </Collapse.Panel>
            </Collapse>
          </Col>
        ))}
        {configuration.dashboard_widgets.length === 0 && (
          <Col>
            <Empty />
          </Col>
        )}
      </Row>
    </CrudContainer>
  );
};
