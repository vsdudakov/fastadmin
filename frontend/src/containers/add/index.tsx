import { SaveOutlined } from "@ant-design/icons";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Breadcrumb,
  Button,
  Col,
  Empty,
  Form,
  Row,
  Space,
  message,
} from "antd";
import type React from "react";
import { useContext } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useParams } from "react-router-dom";

import { CrudContainer } from "@/components/crud-container";
import { FormContainer } from "@/components/form-container";
import { postFetcher } from "@/fetchers/fetchers";
import { getConfigurationModel } from "@/helpers/configuration";
import { handleError } from "@/helpers/forms";
import { getTitleFromModel } from "@/helpers/title";
import { transformDataToServer } from "@/helpers/transform";
import { EModelPermission } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

export const Add: React.FC = () => {
  const [form] = Form.useForm();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { configuration } = useContext(ConfigurationContext);
  const { t: _t } = useTranslation("Add");
  const { model } = useParams();

  const modelConfiguration = getConfigurationModel(
    configuration,
    model as string,
  );

  const {
    mutate,
    isPending: isLoading,
    isError,
  } = useMutation({
    mutationFn: (payload: any) => postFetcher(`/add/${model}`, payload),
    onSuccess: () => {
      message.success(_t("Succesfully added"));

      queryClient.invalidateQueries([`/list/${model}`] as any);
      navigate(`/list/${model}`);
    },
    onError: (error: Error) => {
      handleError(error, form);
    },
  });

  const onFinish = (payload: any) => {
    const data: any = transformDataToServer(payload);
    mutate(data);
  };

  return (
    <CrudContainer
      title={`${_t("Add")} ${
        modelConfiguration && getTitleFromModel(modelConfiguration)
      }`}
      breadcrumbs={
        <Breadcrumb
          items={[
            { title: <Link to="/">{_t("Dashboard")}</Link> },
            {
              title: (
                <Link to={`/list/${model}`}>
                  {modelConfiguration && getTitleFromModel(modelConfiguration)}
                </Link>
              ),
            },
            { title: _t("Add") },
          ]}
        />
      }
    >
      {modelConfiguration?.permissions.includes(EModelPermission.Add) ? (
        <FormContainer
          modelConfiguration={modelConfiguration}
          form={form}
          onFinish={onFinish}
          mode="add"
          hasOperationError={isError}
        >
          <Row justify="end">
            <Col>
              <Space>
                <Button loading={isLoading} htmlType="submit" type="primary">
                  <SaveOutlined /> {_t("Add")}
                </Button>
              </Space>
            </Col>
          </Row>
        </FormContainer>
      ) : (
        <Empty description={_t("No permissions for model")} />
      )}
    </CrudContainer>
  );
};
