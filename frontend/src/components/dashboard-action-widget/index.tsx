import { InfoCircleOutlined, PlayCircleOutlined } from "@ant-design/icons";
import {
  Button,
  Card,
  Col,
  Form,
  Input,
  Radio,
  Row,
  Space,
  Tooltip,
  theme,
} from "antd";
import type React from "react";
import { useCallback, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { postFetcher } from "@/fetchers/fetchers";
import { getTitleFromFieldName } from "@/helpers/title";
import { transformValueToServer } from "@/helpers/transform";
import { getWidgetCls } from "@/helpers/widgets";
import type {
  IModelWidgetAction,
  IWidgetActionArgumentProps,
  IWidgetActionProps,
  IWidgetActionResponse,
} from "@/interfaces/configuration";
import {
  EDashboardWidgetType,
  EFieldWidgetType,
} from "@/interfaces/configuration";

import { ActionJsonResults } from "./action-json-results";
import { ActionTableResults } from "./action-table-results";

interface DashboardActionWidgetProps {
  modelName: string;
  widgetAction: IModelWidgetAction;
}

const { useToken } = theme;

export const hasWidgetValue = (value: any) => {
  if (value === undefined || value === null) {
    return false;
  }
  if (typeof value === "string") {
    return value.trim().length > 0;
  }
  if (Array.isArray(value)) {
    return value.length > 0;
  }
  return true;
};

export const buildWidgetActionQuery = (
  actionArguments: IWidgetActionArgumentProps[],
  values: Record<string, any>,
) =>
  actionArguments
    .filter((arg) => hasWidgetValue(values[arg.name]))
    .map((arg) => ({
      field_name: arg.name,
      widget_type: arg.widget_type,
      value: transformValueToServer(values[arg.name]),
    }));

export const areWidgetValuesEqual = (value: any, expectedValue: any) => {
  const valueIsObject = typeof value === "object" && value !== null;
  const expectedValueIsObject =
    typeof expectedValue === "object" && expectedValue !== null;

  if (valueIsObject || expectedValueIsObject) {
    try {
      return JSON.stringify(value) === JSON.stringify(expectedValue);
    } catch {
      return false;
    }
  }

  return value === expectedValue;
};

export const isWidgetActionArgumentVisible = (
  argument: IWidgetActionArgumentProps,
  values: Record<string, any>,
) => {
  if (!argument.parent_argument) {
    return true;
  }

  return areWidgetValuesEqual(
    values[argument.parent_argument.name],
    argument.parent_argument.value,
  );
};

export const DashboardActionWidget: React.FC<DashboardActionWidgetProps> = ({
  modelName,
  widgetAction,
}) => {
  const { t: _t } = useTranslation("DashboardWidget");
  const { token } = useToken();

  const [filtersForm] = Form.useForm();
  const [filtersState, setFiltersState] = useState<Record<string, any>>({});
  const [isActionRunning, setIsActionRunning] = useState(false);
  const [actionResult, setActionResult] =
    useState<IWidgetActionResponse | null>(null);
  const [resultsView, setResultsView] = useState<"table" | "json">("json");

  const actionArguments: IWidgetActionArgumentProps[] = useMemo(
    () =>
      widgetAction.widget_action_type === EDashboardWidgetType.Action &&
      widgetAction.widget_action_props &&
      "arguments" in widgetAction.widget_action_props
        ? (widgetAction.widget_action_props as IWidgetActionProps).arguments ||
          []
        : [],
    [widgetAction.widget_action_props, widgetAction.widget_action_type],
  );

  const visibleActionArguments = useMemo(
    () =>
      actionArguments.filter((argument) =>
        isWidgetActionArgumentVisible(argument, filtersState),
      ),
    [actionArguments, filtersState],
  );

  const getFilterWidget = useCallback(
    (
      key: string,
      config: IWidgetActionArgumentProps,
      value: any,
      onChange: any,
    ) => {
      const [Widget, widgetProps]: any = getWidgetCls(config.widget_type, _t);

      const onChangeWidget = (widgetValue: any) => {
        switch (Widget) {
          case Input:
          case Input.TextArea:
          case Radio.Group:
            onChange(widgetValue.target.value);
            break;
          default:
            onChange(widgetValue);
            break;
        }
      };

      return (
        <Widget
          placeholder={getTitleFromFieldName(key)}
          {...(widgetProps || {})}
          {...(config.widget_props || {})}
          disableActionButton={
            config.widget_type === EFieldWidgetType.AsyncSelect
          }
          value={value}
          onChange={onChangeWidget}
        />
      );
    },
    [_t],
  );

  const buildQueryFromValues = useCallback(
    (values: Record<string, any>) =>
      buildWidgetActionQuery(
        actionArguments.filter((argument) =>
          isWidgetActionArgumentVisible(argument, values),
        ),
        values,
      ),
    [actionArguments],
  );

  const handleRunAction = async () => {
    const values = await filtersForm.validateFields();
    const currentValues = {
      ...filtersState,
      ...values,
    };
    const nextFiltersState = actionArguments
      .filter((argument) =>
        isWidgetActionArgumentVisible(argument, currentValues),
      )
      .reduce(
        (acc, argument) => {
          acc[argument.name] = currentValues[argument.name];
          return acc;
        },
        {} as Record<string, any>,
      );
    setFiltersState(nextFiltersState);
    setIsActionRunning(true);
    try {
      const query = buildQueryFromValues(currentValues);
      const result = await postFetcher(
        `/widget-action/${modelName}/${widgetAction.name}`,
        {
          query,
        },
      );
      setActionResult(result as IWidgetActionResponse);
      setResultsView("json");
    } finally {
      setIsActionRunning(false);
    }
  };

  const titleNode = (
    <Space size={6}>
      <span>{widgetAction.title}</span>
      {widgetAction.description && (
        <Tooltip title={widgetAction.description}>
          <InfoCircleOutlined style={{ color: token.colorTextSecondary }} />
        </Tooltip>
      )}
    </Space>
  );

  const resultsViewSwitcher = (
    <Space.Compact>
      <Button
        type={resultsView === "table" ? "primary" : "default"}
        onClick={() => setResultsView("table")}
      >
        {_t("Table")}
      </Button>
      <Button
        type={resultsView === "json" ? "primary" : "default"}
        onClick={() => setResultsView("json")}
      >
        {_t("JSON")}
      </Button>
    </Space.Compact>
  );

  return (
    <Card
      title={
        <Row justify="space-between" align="middle">
          <Col>{titleNode}</Col>
        </Row>
      }
      key={`${modelName}-${widgetAction.name}`}
    >
      <Row>
        <Col xs={24}>
          <Form form={filtersForm} onFinish={handleRunAction} layout="vertical">
            {visibleActionArguments.map((arg) => (
              <Form.Item
                key={arg.name}
                name={arg.name}
                preserve={false}
                label={getTitleFromFieldName(arg.name)}
                rules={
                  arg.widget_props?.required
                    ? [
                        {
                          required: true,
                          message: _t("This field is required"),
                        },
                      ]
                    : []
                }
              >
                {getFilterWidget(
                  arg.name,
                  arg,
                  filtersState[arg.name],
                  (nextValue: any) => {
                    setFiltersState((prev) => ({
                      ...prev,
                      [arg.name]: nextValue,
                    }));
                    filtersForm.setFieldValue(arg.name, nextValue);
                  },
                )}
              </Form.Item>
            ))}
            <Row justify="space-between">
              <Col>
                {actionResult?.data?.length ? (
                  <Button
                    danger
                    onClick={() => {
                      setFiltersState({});
                      setActionResult(null);
                    }}
                  >
                    {_t("Reset")}
                  </Button>
                ) : null}
              </Col>
              <Col>
                <Button
                  type="primary"
                  htmlType="submit"
                  loading={isActionRunning}
                  disabled={!hasWidgetValue(filtersState)}
                  icon={<PlayCircleOutlined />}
                >
                  {_t("Run Action")}
                </Button>
              </Col>
            </Row>
          </Form>
        </Col>
      </Row>

      {!isActionRunning &&
        actionResult &&
        (resultsView === "table" ? (
          <ActionTableResults
            actionResult={actionResult}
            toolbarActions={resultsViewSwitcher}
          />
        ) : (
          <ActionJsonResults
            actionResult={actionResult}
            maxHeight={widgetAction.max_height}
            toolbarActions={resultsViewSwitcher}
          />
        ))}
    </Card>
  );
};
