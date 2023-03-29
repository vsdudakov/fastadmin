import React, { useContext } from 'react';
import { useTranslation } from 'react-i18next';
import { Col, Empty, Row } from 'antd';

import { CrudContainer } from 'components/crud-container';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { IDashboardWidget } from 'interfaces/configuration';
import { DashboardWidget } from 'components/dashboard-widget';

export const Index: React.FC = () => {
  const { t: _t } = useTranslation('Dashboard');
  const { configuration } = useContext(ConfigurationContext);
  return (
    <CrudContainer title={_t('Dashboard')}>
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
