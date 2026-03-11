import { SearchOutlined } from "@ant-design/icons";
import { Col, Empty, Input, Row, Tabs } from "antd";
import type React from "react";
import { useContext, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { CrudContainer } from "@/components/crud-container";
import { DashboardActionWidget } from "@/components/dashboard-action-widget";
import { DashboardChartWidget } from "@/components/dashboard-chart-widget";
import {
  EDashboardWidgetType,
  type IModel,
  type IModelWidgetAction,
} from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

export const Index: React.FC = () => {
  const { t: _t } = useTranslation("Dashboard");
  const { configuration } = useContext(ConfigurationContext);
  const [tabsSearch, setTabsSearch] = useState("");

  const widgets = useMemo(
    () =>
      (configuration.models as IModel[]).flatMap((model) =>
        (model.widget_actions || []).map((widgetAction) => ({
          modelName: model.name,
          widgetAction,
        })),
      ),
    [configuration.models],
  );

  const tabItems = useMemo(
    () =>
      Array.from(
        widgets.reduce((acc, widget) => {
          const tabKey = widget.widgetAction.tab || _t("Dashboard");
          const existing = acc.get(tabKey) || [];
          existing.push(widget);
          acc.set(tabKey, existing);
          return acc;
        }, new Map<
          string,
          { modelName: string; widgetAction: IModelWidgetAction }[]
        >()),
      ).map(([tabKey, tabWidgets]) => ({
        key: tabKey,
        label: tabKey,
        widgets: tabWidgets,
      })),
    [_t, widgets],
  );

  const filteredTabItems = useMemo(() => {
    const normalizedQuery = tabsSearch.trim().toLowerCase();

    return tabItems
      .map((tabItem) => {
        const tabWidgets = normalizedQuery
          ? tabItem.widgets.filter(({ widgetAction }) =>
              widgetAction.title.toLowerCase().includes(normalizedQuery),
            )
          : tabItem.widgets;

        // Group widgets by sub_tab within this tab
        const subTabMap = tabWidgets.reduce(
          (
            acc,
            widget: { modelName: string; widgetAction: IModelWidgetAction },
          ) => {
            const key = widget.widgetAction.sub_tab || "";
            const existing = acc.get(key) || [];
            existing.push(widget);
            acc.set(key, existing);
            return acc;
          },
          new Map<
            string,
            { modelName: string; widgetAction: IModelWidgetAction }[]
          >(),
        );

        const subTabs = Array.from(subTabMap.entries());

        const children =
          subTabs.length <= 1 && !subTabs[0]?.[0] ? (
            // No sub-tabs defined: render a single grid as before
            <Row key={`widgets-grid-${tabItem.key}`} gutter={[24, 24]}>
              {tabWidgets.map(({ modelName, widgetAction }) => (
                <Col
                  xs={24}
                  md={widgetAction.width || 24}
                  key={`${modelName}-${widgetAction.name}`}
                >
                  {widgetAction.widget_action_type ===
                  EDashboardWidgetType.Action ? (
                    <DashboardActionWidget
                      modelName={modelName}
                      widgetAction={widgetAction}
                    />
                  ) : (
                    <DashboardChartWidget
                      modelName={modelName}
                      widgetAction={widgetAction}
                    />
                  )}
                </Col>
              ))}
            </Row>
          ) : (
            // At least one sub_tab present: render nested Tabs per sub_tab
            <Tabs
              key={`widgets-sub-tabs-${tabItem.key}`}
              items={subTabs.map(([subTabKey, widgetsInSubTab]) => ({
                key: subTabKey || "_default",
                label: subTabKey || _t("Other"),
                children: (
                  <Row gutter={[24, 24]}>
                    {widgetsInSubTab.map(({ modelName, widgetAction }) => (
                      <Col
                        xs={24}
                        md={widgetAction.width || 24}
                        key={`${modelName}-${widgetAction.name}`}
                      >
                        {widgetAction.widget_action_type ===
                        EDashboardWidgetType.Action ? (
                          <DashboardActionWidget
                            modelName={modelName}
                            widgetAction={widgetAction}
                          />
                        ) : (
                          <DashboardChartWidget
                            modelName={modelName}
                            widgetAction={widgetAction}
                          />
                        )}
                      </Col>
                    ))}
                  </Row>
                ),
              }))}
            />
          );

        return {
          key: tabItem.key,
          label: tabItem.label,
          widgets: tabWidgets,
          children,
        };
      })
      .filter((tabItem) => tabItem.widgets.length > 0);
  }, [_t, tabItems, tabsSearch]);

  return (
    <CrudContainer title={_t("Dashboard")}>
      {widgets.length === 0 && (
        <Empty
          description={_t("No dashboard widgets configured")}
          style={{ padding: "48px 0" }}
        />
      )}
      {widgets.length > 0 && (
        <Tabs
          tabBarExtraContent={{
            right: (
              <Input
                allowClear
                style={{ width: 220, marginBottom: 8 }}
                prefix={<SearchOutlined />}
                placeholder={_t("Search widgets")}
                value={tabsSearch}
                onChange={(event) => setTabsSearch(event.target.value)}
              />
            ),
          }}
          items={filteredTabItems}
        />
      )}
    </CrudContainer>
  );
};
