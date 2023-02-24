import React, { useContext } from 'react';
import { Breadcrumb, Button, Col, Empty, Form, message, Popconfirm, Row, Space } from 'antd';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SaveOutlined, SaveFilled, DeleteOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { CrudContainer } from 'components/crud-container';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { EModelPermission, IModel } from 'interfaces/configuration';
import { deleteFetcher, getFetcher, patchFetcher } from 'fetchers/fetchers';
import { handleError } from 'helpers/forms';
import { transformDataToServer, transformDataFromServer } from 'helpers/transform';
import { FormContainer } from 'components/form-container';

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
        form.setFieldsValue(transformDataFromServer(data));
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
        const next = form.getFieldValue('next');
        if (next) {
          navigate(next);
        }
      },
      onError: (error: Error) => {
        handleError(error, form);
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
    mutate(transformDataToServer(payload));
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
        <Row gutter={[16, 16]}>
          <Col xs={24} xl={14}>
            <FormContainer form={form} onFinish={onFinish}>
              <Row justify="space-between">
                <Col>
                  <Space>
                    <Popconfirm title={_t('Are you sure?')} onConfirm={() => mutateDelete()}>
                      <Button danger>
                        <DeleteOutlined /> {_t('Delete')}
                      </Button>
                    </Popconfirm>
                  </Space>
                </Col>
                <Col>
                  <Space>
                    <Button
                      loading={isLoading || isLoadingInitialValues}
                      onClick={() => {
                        form.submit();
                      }}
                      type="default"
                    >
                      <SaveFilled /> {_t('Save and continue editing')}
                    </Button>
                    <Button
                      loading={isLoading || isLoadingInitialValues}
                      onClick={() => {
                        form.setFieldValue('next', `/add/${model}`);
                        form.submit();
                      }}
                      type="default"
                    >
                      <SaveFilled /> {_t('Save and add another')}
                    </Button>
                    <Button
                      loading={isLoading || isLoadingInitialValues}
                      onClick={() => {
                        form.setFieldValue('next', `/list/${model}`);
                        form.submit();
                      }}
                      type="primary"
                    >
                      <SaveOutlined /> {_t('Save')}
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
