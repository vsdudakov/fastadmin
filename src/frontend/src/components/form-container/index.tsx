import React, { useCallback, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Divider, Form } from 'antd';

import {
  EFieldWidgetType,
  IAddConfigurationField,
  IModel,
  IModelField,
} from 'interfaces/configuration';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { getWidgetCls } from 'helpers/widgets';
import { getTitleFromFieldName } from 'helpers/title';

interface IFormContainer {
  form: any;
  onFinish: (payload: any) => void;
  children: JSX.Element | JSX.Element[];
}

export const FormContainer: React.FC<IFormContainer> = ({ form, onFinish, children }) => {
  const { configuration } = useContext(ConfigurationContext);
  const { t: _t } = useTranslation('FormContainer');
  const { model } = useParams();

  const modelConfiguration: IModel | undefined = configuration.models.find(
    (item: IModel) => item.name === model
  );

  const getWidget = useCallback(
    (addConfiguration: IAddConfigurationField) => {
      if (!addConfiguration.form_widget_type) {
        return null;
      }
      const [Widget, widgetProps]: any = getWidgetCls(addConfiguration.form_widget_type, _t);
      return <Widget {...(widgetProps || {})} {...(addConfiguration.form_widget_props || {})} />;
    },
    [_t]
  );

  const formItems = useCallback(() => {
    const fields = (modelConfiguration || { fields: [] }).fields;
    return fields
      .filter((field: IModelField) => !!field.add_configuration?.form_widget_type)
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
            ].includes(field.add_configuration?.form_widget_type as EFieldWidgetType)
              ? 'checked'
              : undefined
          }
        >
          {getWidget(field.add_configuration as IAddConfigurationField)}
        </Form.Item>
      ));
  }, [getWidget, modelConfiguration]);

  return (
    <Form layout="vertical" form={form} onFinish={onFinish}>
      {modelConfiguration?.save_on_top && (
        <>
          {children}
          <Divider />
        </>
      )}
      {formItems()}
      <Divider />
      {children}
    </Form>
  );
};
