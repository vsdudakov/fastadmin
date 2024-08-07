import { Col, Collapse, Divider, Form, Row } from "antd";
import type React from "react";
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { InlineWidget } from "@/components/inline-widget";
import { getTitleFromFieldName, getTitleFromModel } from "@/helpers/title";
import { isJson, isSlug } from "@/helpers/transform";
import { getWidgetCls } from "@/helpers/widgets";
import {
  EFieldWidgetType,
  type IAddConfigurationField,
  type IChangeConfigurationField,
  type IInlineModel,
  type IModel,
  type IModelField,
} from "@/interfaces/configuration";

interface IFormContainer {
  modelConfiguration: IModel;
  id?: string;

  form: any;

  onFinish: (payload: any) => void;
  children: React.ReactNode;
  mode: "add" | "change" | "inline-add" | "inline-change";
  hasOperationError?: boolean;

  initialValues?: Record<string, any>;
}

export const FormContainer: React.FC<IFormContainer> = ({
  modelConfiguration,
  id,
  form,
  onFinish,
  children,
  mode,
  hasOperationError,
  initialValues,
}) => {
  const { t: _t } = useTranslation("FormContainer");

  const [activeKey, setActiveKey] = useState<string[]>(
    (modelConfiguration?.fieldsets || [])
      .filter((fieldset) => !(fieldset[1]?.classes || []).includes("collapse"))
      .map((fieldset) => JSON.stringify(fieldset[1]?.fields)),
  );

  useEffect(() => {
    if (hasOperationError) {
      setActiveKey(
        (modelConfiguration?.fieldsets || []).map((fieldset) =>
          JSON.stringify(fieldset[1]?.fields),
        ),
      );
    }
  }, [hasOperationError, modelConfiguration?.fieldsets]);

  useEffect(() => {
    form.setFieldsValue(initialValues);
  }, [form, initialValues]);

  const getWidget = useCallback(
    (
      configurationField: IAddConfigurationField | IChangeConfigurationField,
    ) => {
      if (!configurationField.form_widget_type) {
        return null;
      }

      const [Widget, widgetProps]: any = getWidgetCls(
        configurationField.form_widget_type,
        _t,
        id,
      );
      return (
        <Widget
          {...(widgetProps || {})}
          {...(configurationField.form_widget_props || {})}
        />
      );
    },
    [_t, id],
  );

  const getConf = useCallback(
    (field: IModelField) => {
      if (mode === "change" || mode === "inline-change") {
        return field?.change_configuration || {};
      }
      return field?.add_configuration || {};
    },
    [mode],
  );

  const formItemWidgets = useCallback(
    (formFields: IModelField[]) => {
      return formFields.map((field: IModelField) => (
        <Form.Item
          key={field.name}
          name={field.name}
          label={getTitleFromFieldName(field.name)}
          rules={
            [
              ...(getConf(field).required
                ? [
                    {
                      required: true,
                    },
                  ]
                : []),
              ...(getConf(field).form_widget_type ===
              EFieldWidgetType.EmailInput
                ? [
                    {
                      type: "email",
                    },
                  ]
                : []),
              ...(getConf(field).form_widget_type === EFieldWidgetType.UrlInput
                ? [
                    {
                      type: "url",
                    },
                  ]
                : []),
              ...(getConf(field).form_widget_type ===
              EFieldWidgetType.JsonTextArea
                ? [
                    {
                      validator: async (_: any, value: string) => {
                        if (!isJson(value)) {
                          throw new Error(_t("Invalid JSON") as string);
                        }
                      },
                    },
                  ]
                : []),
              ...(getConf(field).form_widget_type === EFieldWidgetType.SlugInput
                ? [
                    {
                      validator: async (_: any, value: string) => {
                        if (!isSlug(value)) {
                          throw new Error(
                            _t(
                              "Invalid Slug. Please use lowercase letters, numbers, and hyphens.",
                            ) as string,
                          );
                        }
                      },
                    },
                  ]
                : []),
            ] as any
          }
          valuePropName={
            [
              EFieldWidgetType.Checkbox,
              EFieldWidgetType.Switch,
              EFieldWidgetType.CheckboxGroup,
            ].includes(getConf(field).form_widget_type as EFieldWidgetType)
              ? "checked"
              : undefined
          }
        >
          {getWidget(getConf(field))}
        </Form.Item>
      ));
    },
    [_t, getConf, getWidget],
  );

  const formItems = useCallback(() => {
    const fields = (modelConfiguration?.fields || [])
      .filter((field: IModelField) => !!getConf(field).form_widget_type)
      .filter((field: IModelField) => {
        if (mode === "add" || mode === "inline-add") {
          // exclude readonly fields from add form
          return (
            !field.add_configuration?.form_widget_props?.disabled &&
            !field.add_configuration?.form_widget_props?.readOnly
          );
        }
        return true;
      });
    const fieldsets = modelConfiguration?.fieldsets || [];
    if (fieldsets.length > 0) {
      const onChange = (key: string[]) => setActiveKey(key);
      return (
        <Collapse
          size="small"
          expandIconPosition="end"
          activeKey={activeKey}
          onChange={onChange as any}
          items={fieldsets.map((fieldset) => {
            const collapseTitle = fieldset[0];
            const collapseFields = fieldset[1]?.fields;
            return {
              key: JSON.stringify(collapseFields),
              label: collapseTitle || _t("General"),
              children: formItemWidgets(
                fields
                  .filter((field: IModelField) =>
                    (collapseFields || []).includes(field.name),
                  )
                  .sort(
                    (a: IModelField, b: IModelField) =>
                      collapseFields.indexOf(a.name) -
                      collapseFields.indexOf(b.name),
                  ),
              ),
            };
          })}
        />
      );
    }
    return formItemWidgets(
      fields.sort(
        (a: IModelField, b: IModelField) =>
          (getConf(a).index || 0) - (getConf(b).index || 0),
      ),
    );
  }, [
    _t,
    activeKey,
    formItemWidgets,
    getConf,
    modelConfiguration?.fields,
    modelConfiguration?.fieldsets,
    mode,
  ]);

  const inlineItems = useCallback(() => {
    if (!id) {
      return null;
    }
    return (modelConfiguration?.inlines || []).map((inline: IInlineModel) => {
      return (
        <Form.Item label={getTitleFromModel(inline, true)} key={inline.name}>
          <InlineWidget modelConfiguration={inline} parentId={id} />
        </Form.Item>
      );
    });
  }, [modelConfiguration?.inlines, id]);

  return (
    <Form
      initialValues={initialValues}
      layout="vertical"
      form={form}
      onFinish={onFinish}
    >
      {modelConfiguration?.save_on_top && (
        <>
          {children}
          <Divider />
        </>
      )}
      <Row gutter={[32, 32]}>
        <Col
          xs={24}
          xl={mode === "inline-add" || mode === "inline-change" ? 24 : 12}
        >
          {formItems()}
        </Col>
        {mode === "change" && (
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
