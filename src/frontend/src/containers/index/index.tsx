import React from 'react';
import { useTranslation } from 'react-i18next';
import { Breadcrumb, Empty } from 'antd';
import { Link } from 'react-router-dom';

import { CrudContainer } from 'components/crud-container';

export const Index: React.FC = () => {
  const { t: _t } = useTranslation('Dashboard');
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
      <Empty />
    </CrudContainer>
  );
};
