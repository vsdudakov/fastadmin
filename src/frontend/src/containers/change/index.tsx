import React, { useContext } from 'react';
import { Breadcrumb, Button, Col, Empty, Form, message, Popconfirm, Row, Space } from 'antd';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SaveOutlined, SaveFilled, DeleteOutlined } from '@ant-design/icons';

import { CrudContainer } from 'components/crud-container';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import {
  EModelPermission,
  IChangeConfigurationField,
  IModel,
  IModelField,
} from 'interfaces/configuration';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { deleteFetcher, getFetcher, patchFetcher } from 'fetchers/fetchers';
import { setFormErrors } from 'helpers/forms';
import { getWidgetCls } from 'helpers/widgets';

export const Change: React.FC = () => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { configuration } = useContext(ConfigurationContext);
  const { t: _t } = useTranslation('Change');
  const { model, id } = useParams();

  const modelConfiguration: IModel | undefined = configuration.models.find(
    (item: IModel) => item.name === model
  );

  const { isLoading: isLoadingInitialValues } = useQuery(
    [`/retrieve/${model}/${id}`],
    () => getFetcher(`/retrieve/${model}/${id}`),
    {
      onSuccess: (data) => {
        form.setFieldsValue(data);
      },
    }
  );

  const { mutate, isLoading } = useMutation(
    (payload: any) => patchFetcher(`/change/${model}/${id}`, payload),
    {
      onSuccess: () => {
        message.success(_t('Succesfully updated'));
        queryClient.invalidateQueries([`/retrieve/${model}/${id}`]);
        queryClient.invalidateQueries([`/list/${model}`]);
        const value = form.getFieldValue('save_and_close');
        if (value) {
          navigate(`/list/${model}`);
        }
      },
      onError: (error: Error) => {
        setFormErrors(form, error);
      },
    }
  );

  const { mutate: mutateDelete } = useMutation(() => deleteFetcher(`/delete/${model}/${id}`), {
    onSuccess: () => {
      message.success(_t('Successfully deleted'));
      queryClient.invalidateQueries([`/list/${model}`]);
      navigate(`/list/${model}`);
    },
    onError: () => {
      message.error(_t('Server error'));
    },
  });

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
      title={`${_t('Change')} ${model} ${id}`}
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
      {modelConfiguration && modelConfiguration.permissions.includes(EModelPermission.Change) ? (
        <Form form={form} onFinish={onFinish}>
          {modelConfiguration.fields
            .filter((field: IModelField) => !!field.change_configuration?.widget_type)
            .map((field: IModelField) => (
              <Form.Item key={field.name} name={field.name}>
                {getWidget(field.change_configuration as IChangeConfigurationField)}
              </Form.Item>
            ))}
          <Row justify="space-between">
            <Col>
              <Space>
                <Form.Item>
                  <Popconfirm title={_t('Are you sure?')} onConfirm={() => mutateDelete()}>
                    <Button danger>
                      <DeleteOutlined /> {_t('Delete')}
                    </Button>
                  </Popconfirm>
                </Form.Item>
              </Space>
            </Col>
            <Col>
              <Space>
                <Form.Item>
                  <Button
                    loading={isLoading || isLoadingInitialValues}
                    onClick={() => {
                      form.setFieldValue('save_and_close', true);
                      form.submit();
                    }}
                    type="default"
                  >
                    <SaveFilled /> {_t('Save And Close')}
                  </Button>
                </Form.Item>
                <Form.Item>
                  <Button
                    loading={isLoading || isLoadingInitialValues}
                    htmlType="submit"
                    type="primary"
                  >
                    <SaveOutlined /> {_t('Save')}
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
