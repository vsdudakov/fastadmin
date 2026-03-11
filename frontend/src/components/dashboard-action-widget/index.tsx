import {
  CopyOutlined,
  ExpandOutlined,
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
  Modal,
  message,
  Radio,
  Row,
  Space,
  Tooltip,
  theme,
} from "antd";
import React, { useCallback, useMemo, useState } from "react";
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

const escapeRegExp = (value: string) =>
  value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

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
  const [isResultsModalVisible, setIsResultsModalVisible] = useState(false);

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

  const highlightedResults = useMemo(() => {
    const json = JSON.stringify(filteredData, null, 2);

    if (!searchTerm.trim()) {
      return json;
    }

    const term = searchTerm.toLowerCase();
    const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, "gi");
    const parts = json.split(regex);

    return parts.map((part, index) => {
      const key = `${part}-${index}`;
      return part.toLowerCase() === term ? (
        <mark key={key}>{part}</mark>
      ) : (
        <React.Fragment key={key}>{part}</React.Fragment>
      );
    });
  }, [filteredData, searchTerm]);

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
        <>
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
                  <Space>
                    <Tooltip title={_t("Expand results")}>
                      <Button
                        type="default"
                        onClick={() => setIsResultsModalVisible(true)}
                        icon={<ExpandOutlined />}
                      />
                    </Tooltip>
                    <Tooltip title={_t("Copy to clipboard")}>
                      <Button
                        type="primary"
                        onClick={handleCopyResults}
                        icon={<CopyOutlined />}
                      />
                    </Tooltip>
                  </Space>
                </Col>
              </Row>
              <pre
                style={{
                  marginTop: 12,
                  maxHeight: widgetAction.max_height || 240,
                  overflow: "auto",
                  background: "#fafafa",
                  padding: 8,
                  borderRadius: 4,
                  border: "1px solid #f0f0f0",
                }}
              >
                {highlightedResults}
              </pre>
            </Col>
          </Row>
          <Modal
            open={isResultsModalVisible}
            title={_t("Action results")}
            onCancel={() => setIsResultsModalVisible(false)}
            footer={null}
            width="100%"
            style={{ top: 0, paddingBottom: 0, marginTop: 20 }}
            styles={{ body: { paddingTop: 0 } }}
          >
            <Space
              orientation="vertical"
              style={{ width: "100%" }}
              size="middle"
            >
              <Row justify="start" align="middle">
                <Col xs={20}>
                  <Input.Search
                    style={{ marginTop: 12 }}
                    placeholder={_t("Search results")}
                    onSearch={(value) => setSearchTerm(value)}
                    defaultValue={searchTerm}
                    enterButton
                  />
                </Col>
              </Row>
              <pre
                style={{
                  flex: 1,
                  maxHeight: "calc(100vh - 300px)",
                  overflow: "auto",
                  background: "#fafafa",
                  padding: 12,
                  borderRadius: 4,
                  border: "1px solid #f0f0f0",
                }}
              >
                {highlightedResults}
              </pre>
              <Row justify="end">
                <Col>
                  <Tooltip title={_t("Copy to clipboard")}>
                    <Button
                      type="primary"
                      onClick={handleCopyResults}
                      icon={<CopyOutlined />}
                    />
                  </Tooltip>
                </Col>
              </Row>
            </Space>
          </Modal>
        </>
      )}
    </Card>
  );
};
