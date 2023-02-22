import React from 'react';
import { Breadcrumb } from 'antd';
import { Link, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';

import { CrudContainer } from 'components/crud-container';

export const History: React.FC = () => {
  const { t: _t } = useTranslation('History');
  const { model, id } = useParams();
  return (
    <CrudContainer
      title={_t('Change Model Item')}
      breadcrumbs={
        <Breadcrumb>
          <Breadcrumb.Item>
            <Link to="/">{_t('Dashboard')}</Link>
          </Breadcrumb.Item>
          <Breadcrumb.Item>
            <Link to={`/list/${model}`}>{model}</Link>
          </Breadcrumb.Item>
          <Breadcrumb.Item>{id}</Breadcrumb.Item>
        </Breadcrumb>
      }
    >
      <div>
        {model} {id}
      </div>
    </CrudContainer>
  );
};
