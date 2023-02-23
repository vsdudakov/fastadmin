import React, { useCallback, useContext } from 'react';
import { Breadcrumb, Button, Col, Empty, Form, message, Popconfirm, Row, Space } from 'antd';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { SaveOutlined, SaveFilled, DeleteOutlined } from '@ant-design/icons';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { CrudContainer } from 'components/crud-container';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import {
  EFieldWidgetType,
  EModelPermission,
  IChangeConfigurationField,
  IModel,
  IModelField,
} from 'interfaces/configuration';
import { deleteFetcher, getFetcher, patchFetcher } from 'fetchers/fetchers';
import { setFormErrors } from 'helpers/forms';
import { getWidgetCls } from 'helpers/widgets';
import { getTitleFromFieldName } from 'helpers/title';
import { transformDataToServer, transformDataFromServer } from 'helpers/transform';

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
    mutate(transformDataToServer(payload));
  };

  const getWidget = useCallback(
    (changeConfiguration: IChangeConfigurationField) => {
      if (!changeConfiguration.widget_type) {
        return null;
      }
      const [Widget, widgetProps]: any = getWidgetCls(changeConfiguration.widget_type, _t);
      return <Widget {...(widgetProps || {})} {...(changeConfiguration.widget_props || {})} />;
    },
    [_t]
  );

  const formItems = useCallback(
    (col: number) => {
      const fields = (modelConfiguration || { fields: [] }).fields;
      return fields
        .filter((field: IModelField) => !!field.change_configuration?.widget_type)
        .filter(
          (field: IModelField) =>
            field.change_configuration?.col === col ||
            (col === 1 && !field.change_configuration?.col)
        )
        .sort(
          (a: IModelField, b: IModelField) =>
            (a?.change_configuration?.row || 0) - (b?.change_configuration?.row || 0)
        )
        .map((field: IModelField) => (
          <Form.Item
            key={field.name}
            name={field.name}
            label={getTitleFromFieldName(field.name)}
            rules={
              field.change_configuration?.required
                ? [
                    {
                      required: true,
                    },
                  ]
                : []
            }
            valuePropName={
              [
                EFieldWidgetType.Checkbox,
                EFieldWidgetType.Switch,
                EFieldWidgetType.CheckboxGroup,
              ].includes(field.add_configuration?.widget_type as EFieldWidgetType)
                ? 'checked'
                : undefined
            }
          >
            {getWidget(field.change_configuration as IChangeConfigurationField)}
          </Form.Item>
        ));
    },
    [getWidget, modelConfiguration]
  );

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
        <Form layout="vertical" form={form} onFinish={onFinish}>
          <Row gutter={[16, 16]}>
            <Col xs={24} xl={8}>
              {formItems(1)}
            </Col>
            <Col xs={24} xl={8}>
              {formItems(2)}
            </Col>
            <Col xs={24} xl={8}>
              {formItems(3)}
            </Col>
          </Row>
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
