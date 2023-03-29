import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { Breadcrumb, Col, Empty, Row } from 'antd';
import { Link } from 'react-router-dom';

import { CrudContainer } from 'components/crud-container';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { IDashboardWidget } from 'interfaces/configuration';
import { DashboardWidget } from 'components/dashboard-widget';

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
            <DashboardWidget widget={widget} />
          </Col>
        ))}
      </Row>
      {configuration.dashboard_widgets.length === 0 && <Empty />}
    </CrudContainer>
  );
};
