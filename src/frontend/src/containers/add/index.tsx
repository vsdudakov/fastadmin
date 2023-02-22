import React from 'react';
import { Link, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { CrudContainer } from 'components/crud-container';
import { Breadcrumb } from 'antd';

export const Add: React.FC = () => {
  const { t: _t } = useTranslation('Add');
  const { model } = useParams();
  return (
    <CrudContainer
      title={_t('Add Model Item')}
      breadcrumbs={
        <Breadcrumb>
          <Breadcrumb.Item>
            <Link to="/">{_t('Dashboard')}</Link>
          </Breadcrumb.Item>
          <Breadcrumb.Item>
            <Link to={`/list/${model}`}>{model}</Link>
          </Breadcrumb.Item>
          <Breadcrumb.Item>{_t('Add')}</Breadcrumb.Item>
        </Breadcrumb>
      }
    >
      <div>{model}</div>
    </CrudContainer>
  );
};
