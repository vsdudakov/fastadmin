import React, { useCallback, useContext } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Collapse, Divider, Form } from 'antd';

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
  mode: 'add' | 'change';
}

export const FormContainer: React.FC<IFormContainer> = ({ form, onFinish, children, mode }) => {
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

  const getConf = useCallback(
    (field: IModelField) => {
      if (mode === 'change') {
        return field?.change_configuration || {};
      }
      return field?.add_configuration || {};
    },
    [mode]
  );

  const formItemWidgets = useCallback(
    (formFields: IModelField[]) => {
      return formFields
        .sort((a: IModelField, b: IModelField) => (getConf(a).index || 0) - (getConf(b).index || 0))
        .map((field: IModelField) => (
          <Form.Item
            key={field.name}
            name={field.name}
            label={getTitleFromFieldName(field.name)}
            rules={
              getConf(field).required
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
              ].includes(getConf(field).form_widget_type as EFieldWidgetType)
                ? 'checked'
                : undefined
            }
          >
            {getWidget(getConf(field))}
          </Form.Item>
        ));
    },
    [getConf, getWidget]
  );

  const formItems = useCallback(() => {
    const fields = (modelConfiguration?.fields || []).filter(
      (field: IModelField) => !!getConf(field).form_widget_type
    );
    const fieldsets = modelConfiguration?.fieldsets || [];
    if (fieldsets.length > 0) {
      const defaultActiveKey = fieldsets
        .filter((fieldset) => !(fieldset[1]?.classes || []).includes('collapse'))
        .map((fieldset) => JSON.stringify(fieldset[1]?.fields));
      return (
        <Collapse defaultActiveKey={defaultActiveKey}>
          {fieldsets.map((fieldset) => {
            const collapseTitle = fieldset[0];
            const collapseFields = fieldset[1]?.fields;
            return (
              <Collapse.Panel header={collapseTitle || ''} key={JSON.stringify(collapseFields)}>
                {formItemWidgets(
                  fields.filter((field: IModelField) => (collapseFields || []).includes(field.name))
                )}
              </Collapse.Panel>
            );
          })}
        </Collapse>
      );
    }

    return formItemWidgets(fields);
  }, [formItemWidgets, modelConfiguration?.fields, modelConfiguration?.fieldsets]);

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
