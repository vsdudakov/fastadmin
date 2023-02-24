import React, { useContext } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Breadcrumb, Button, Col, Empty, Form, message, Row, Space } from 'antd';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { SaveOutlined } from '@ant-design/icons';

import { CrudContainer } from 'components/crud-container';
import { EModelPermission, IModel } from 'interfaces/configuration';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { postFetcher } from 'fetchers/fetchers';
import { setFormErrors } from 'helpers/forms';
import { transformDataToServer } from 'helpers/transform';
import { FormContainer } from 'components/form-container';

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
    mutate(transformDataToServer(payload));
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
        <Row gutter={[16, 16]}>
          <Col xs={24} xl={14}>
            <FormContainer form={form} onFinish={onFinish}>
              <Row justify="end">
                <Col>
                  <Space>
                    <Button loading={isLoading} htmlType="submit" type="primary">
                      <SaveOutlined /> {_t('Add')}
                    </Button>
                  </Space>
                </Col>
              </Row>
            </FormContainer>
          </Col>
        </Row>
      ) : (
        <Empty description={_t('No permissions for model')} />
      )}
    </CrudContainer>
  );
};
