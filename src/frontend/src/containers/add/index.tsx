import React, { useContext } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Breadcrumb, Button, Col, Empty, Form, message, Row, Space } from 'antd';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { SaveOutlined } from '@ant-design/icons';

import { CrudContainer } from 'components/crud-container';
import {
  EModelPermission,
  IChangeConfigurationField,
  IModel,
  IModelField,
} from 'interfaces/configuration';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { postFetcher } from 'fetchers/fetchers';
import { setFormErrors } from 'helpers/forms';
import { getWidgetCls } from 'helpers/widgets';

export const Add: React.FC = () => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { configuration } = useContext(ConfigurationContext);
  const { t: _t } = useTranslation('Add');
  const { model } = useParams();

  const modelConfiguration: IModel | undefined = configuration.models.find(
    (item: IModel) => item.name === model
  );

  const { mutate, isLoading } = useMutation(
    (payload: any) => postFetcher(`/add/${model}`, payload),
    {
      onSuccess: (data, payload) => {
        message.success(_t('Succesfully created'));
        queryClient.invalidateQueries([`/list/${model}`]);
        navigate(`/list/${model}`);
      },
      onError: (error: Error) => {
        setFormErrors(form, error);
      },
    }
  );

  const onFinish = (payload: any) => {
    mutate(payload);
  };

  const getWidget = (changeConfiguration: IChangeConfigurationField) => {
    if (!changeConfiguration.widget_type) {
      return null;
    }
    const [Widget, widgetProps]: any = getWidgetCls(changeConfiguration.widget_type, _t);
    return <Widget {...(widgetProps || {})} {...(changeConfiguration.widget_props || {})} />;
  };

  return (
    <CrudContainer
      title={`${_t('Add')} ${model}`}
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
      {modelConfiguration && modelConfiguration.permissions.includes(EModelPermission.Add) ? (
        <Form form={form} onFinish={onFinish}>
          {modelConfiguration.fields
            .filter((field: IModelField) => !!field.add_configuration)
            .map((field: IModelField) => (
              <Form.Item key={field.name} name={field.name}>
                {getWidget(field.change_configuration as IChangeConfigurationField)}
              </Form.Item>
            ))}
          <Row justify="end">
            <Col>
              <Space>
                <Form.Item>
                  <Button loading={isLoading} htmlType="submit" type="primary">
                    <SaveOutlined /> {_t('Add')}
                  </Button>
                </Form.Item>
              </Space>
            </Col>
          </Row>
        </Form>
      ) : (
        <Empty description={_t('No permissions for model')} />
      )}
    </CrudContainer>
  );
};
