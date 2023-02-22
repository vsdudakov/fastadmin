import React, { useContext } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Breadcrumb, Empty, Table } from 'antd';

import { CrudContainer } from 'components/crud-container';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { IModel, IModelField } from 'interfaces/configuration';

export const List: React.FC = () => {
  const { configuration } = useContext(ConfigurationContext);
  const { t: _t } = useTranslation('List');
  const { model } = useParams();

  const modelConfiguration: IModel | undefined = configuration.models.find(
    (item: IModel) => item.name === model
  );

  return (
    <CrudContainer
      title={_t('Model Items')}
      breadcrumbs={
        <Breadcrumb>
          <Breadcrumb.Item>
            <Link to="/">{_t('Dashboard')}</Link>
          </Breadcrumb.Item>
          <Breadcrumb.Item>{model}</Breadcrumb.Item>
        </Breadcrumb>
      }
    >
      {modelConfiguration ? (
        <Table
          columns={modelConfiguration.fields.map((field: IModelField) => {
            return {};
          })}
        />
      ) : (
        <Empty description={_t('No registered model')} />
      )}
    </CrudContainer>
  );
};
