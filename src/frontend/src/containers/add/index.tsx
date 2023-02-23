import React, { useCallback, useContext } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Breadcrumb, Button, Col, Empty, Form, message, Row, Space } from 'antd';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { SaveOutlined } from '@ant-design/icons';

import { CrudContainer } from 'components/crud-container';
import {
  EFieldWidgetType,
  EModelPermission,
  IAddConfigurationField,
  IModel,
  IModelField,
} from 'interfaces/configuration';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { postFetcher } from 'fetchers/fetchers';
import { setFormErrors } from 'helpers/forms';
import { getWidgetCls } from 'helpers/widgets';
import { getTitleFromFieldName } from 'helpers/title';
import { transformDataToServer } from 'helpers/transform';

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

  const getWidget = useCallback(
    (addConfiguration: IAddConfigurationField) => {
      if (!addConfiguration.widget_type) {
        return null;
      }
      const [Widget, widgetProps]: any = getWidgetCls(addConfiguration.widget_type, _t);
      return <Widget {...(widgetProps || {})} {...(addConfiguration.widget_props || {})} />;
    },
    [_t]
  );

  const formItems = useCallback(
    (col: number) => {
      const fields = (modelConfiguration || { fields: [] }).fields;
      return fields
        .filter((field: IModelField) => !!field.add_configuration?.widget_type)
        .filter(
          (field: IModelField) =>
            field.add_configuration?.col === col || (col === 1 && !field.add_configuration?.col)
        )
        .sort(
          (a: IModelField, b: IModelField) =>
            (a?.add_configuration?.row || 0) - (b?.add_configuration?.row || 0)
        )
        .map((field: IModelField) => (
          <Form.Item
            key={field.name}
            name={field.name}
            label={getTitleFromFieldName(field.name)}
            rules={
              field.add_configuration?.required
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
                EFieldWidgetType.RadioGroup,
              ].includes(field.add_configuration?.widget_type as EFieldWidgetType)
                ? 'checked'
                : undefined
            }
          >
            {getWidget(field.add_configuration as IAddConfigurationField)}
          </Form.Item>
        ));
    },
    [getWidget, modelConfiguration]
  );

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
