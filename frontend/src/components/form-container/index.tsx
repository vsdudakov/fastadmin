import React, { useCallback, useContext, useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Col, Collapse, Divider, Form, Row } from 'antd';

import {
  EFieldWidgetType,
  IAddConfigurationField,
  IChangeConfigurationField,
  IModel,
  IModelField,
  IInlineModel,
} from 'interfaces/configuration';
import { ConfigurationContext } from 'providers/ConfigurationProvider';
import { getWidgetCls } from 'helpers/widgets';
import { getTitleFromFieldName, getTitleFromModelClass } from 'helpers/title';
import { InlineWidget } from 'components/inline-widget';

interface IFormContainer {
  form: any;
  onFinish: (payload: any) => void;
  children: JSX.Element | JSX.Element[];
  mode: 'add' | 'change';
  hasOperationError?: boolean;
}

export const FormContainer: React.FC<IFormContainer> = ({
  form,
  onFinish,
  children,
  mode,
  hasOperationError,
}) => {
  const { configuration } = useContext(ConfigurationContext);
  const { t: _t } = useTranslation('FormContainer');
  const { model } = useParams();

  const modelConfiguration: IModel | undefined = configuration.models.find(
    (item: IModel) => item.name === model
  );

  const [activeKey, setActiveKey] = useState<string[]>(
    (modelConfiguration?.fieldsets || [])
      .filter((fieldset) => !(fieldset[1]?.classes || []).includes('collapse'))
      .map((fieldset) => JSON.stringify(fieldset[1]?.fields))
  );

  useEffect(() => {
    if (hasOperationError) {
      setActiveKey(
        (modelConfiguration?.fieldsets || []).map((fieldset) => JSON.stringify(fieldset[1]?.fields))
      );
    }
  }, [hasOperationError, modelConfiguration?.fieldsets, setActiveKey]);

  const getWidget = useCallback(
    (configurationField: IAddConfigurationField | IChangeConfigurationField) => {
      if (!configurationField.form_widget_type) {
        return null;
      }
      const [Widget, widgetProps]: any = getWidgetCls(configurationField.form_widget_type, _t);
      return <Widget {...(widgetProps || {})} {...(configurationField.form_widget_props || {})} />;
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
      const onChange = (key: string[]) => setActiveKey(key);
      return (
        <Collapse
          size="small"
          expandIconPosition="end"
          activeKey={activeKey}
          onChange={onChange as any}
        >
          {fieldsets.map((fieldset) => {
            const collapseTitle = fieldset[0];
            const collapseFields = fieldset[1]?.fields;
            return (
              <Collapse.Panel
                header={collapseTitle || _t('General')}
                key={JSON.stringify(collapseFields)}
              >
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
  }, [
    _t,
    activeKey,
    formItemWidgets,
    getConf,
    modelConfiguration?.fields,
    modelConfiguration?.fieldsets,
  ]);

  const inlineItems = useCallback(() => {
    return (modelConfiguration?.inlines || []).map((inline: IInlineModel) => {
      return (
        <Form.Item
          label={
            inline.verbose_name_plural ||
            `${inline.verbose_name || getTitleFromModelClass(inline.name)}s`
          }
          key={inline.name}
        >
          <InlineWidget modelConfiguration={inline} />
        </Form.Item>
      );
    });
  }, [modelConfiguration?.inlines]);

  return (
    <Form layout="vertical" form={form} onFinish={onFinish}>
      {modelConfiguration?.save_on_top && (
        <>
          {children}
          <Divider />
        </>
      )}
      <Row gutter={[32, 32]}>
        <Col xs={24} xl={12}>
          {formItems()}
        </Col>
        {mode === 'change' && (
          <Col xs={24} xl={12}>
            {inlineItems()}
          </Col>
        )}
      </Row>
      <Divider />
      {children}
    </Form>
  );
};
