import {
  CopyOutlined,
  InfoCircleOutlined,
  PlayCircleOutlined,
} from "@ant-design/icons";
import {
  Button,
  Card,
  Col,
  Divider,
  Form,
  Input,
  message,
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
import { EDashboardWidgetType } from "@/interfaces/configuration";

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
  const [searchTerm, setSearchTerm] = useState("");

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
          value={value}
          onChange={onChangeWidget}
        />
      );
    },
    [_t],
  );

  const buildQueryFromValues = useCallback(
    (values: Record<string, any>) =>
      buildWidgetActionQuery(actionArguments, values),
    [actionArguments],
  );

  const handleRunAction = async () => {
    const values = await filtersForm.validateFields();
    setFiltersState(values);
    setIsActionRunning(true);
    try {
      const query = buildQueryFromValues(values);
      const result = await postFetcher(
        `/widget-action/${modelName}/${widgetAction.name}`,
        {
          query,
        },
      );
      setActionResult(result as IWidgetActionResponse);
      setSearchTerm("");
    } finally {
      setIsActionRunning(false);
    }
  };

  const filteredData = useMemo(() => {
    if (!actionResult) {
      return [];
    }
    if (!searchTerm.trim()) {
      return actionResult.data;
    }
    const term = searchTerm.toLowerCase();
    return actionResult.data.filter((row) =>
      JSON.stringify(row).toLowerCase().includes(term),
    );
  }, [actionResult, searchTerm]);

  const handleCopyResults = async () => {
    /* v8 ignore next -- button not rendered when result is missing */
    if (!actionResult) {
      return;
    }
    await navigator.clipboard.writeText(JSON.stringify(filteredData, null, 2));
    message.success(_t("Results copied to clipboard"));
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
            {actionArguments.map((arg) => (
              <Form.Item
                key={arg.name}
                name={arg.name}
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
                  (nextValue: any) =>
                    setFiltersState((prev) => ({
                      ...prev,
                      [arg.name]: nextValue,
                    })),
                )}
              </Form.Item>
            ))}
            <Row justify="space-between">
              <Col>
                {filteredData.length > 0 && (
                  <Button
                    danger
                    onClick={() => {
                      setFiltersState({});
                      setSearchTerm("");
                      setActionResult(null);
                    }}
                  >
                    {_t("Reset")}
                  </Button>
                )}
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

      {!isActionRunning && actionResult && (
        <Row>
          <Divider />
          <Col xs={24}>
            <Row justify="space-between">
              <Col xs={12}>
                <Input.Search
                  placeholder={_t("Search results")}
                  onSearch={(value) => setSearchTerm(value)}
                  enterButton
                />
              </Col>
              <Col>
                <Button
                  type="primary"
                  onClick={handleCopyResults}
                  icon={<CopyOutlined />}
                >
                  {_t("Copy to clipboard")}
                </Button>
              </Col>
            </Row>
            <pre
              style={{
                marginTop: 12,
                maxHeight: 240,
                overflow: "auto",
                background: "#fafafa",
                padding: 8,
                borderRadius: 4,
                border: "1px solid #f0f0f0",
              }}
            >
              {JSON.stringify(filteredData, null, 2)}
            </pre>
          </Col>
        </Row>
      )}
    </Card>
  );
};
