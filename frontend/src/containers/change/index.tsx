import { DeleteOutlined, SaveFilled, SaveOutlined } from "@ant-design/icons";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Breadcrumb,
  Button,
  Col,
  Empty,
  Form,
  Popconfirm,
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
import {
  deleteFetcher,
  getFetcher,
  patchFetcher,
  postFetcher,
} from "@/fetchers/fetchers";
import { getConfigurationModel } from "@/helpers/configuration";
import { handleError } from "@/helpers/forms";
import { getTitleFromModel } from "@/helpers/title";
import {
  transformDataFromServer,
  transformDataToServer,
} from "@/helpers/transform";
import { useIsMobile } from "@/hooks/useIsMobile";
import { EModelPermission } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

export const Change: React.FC = () => {
  const [form] = Form.useForm();
  const isMobile = useIsMobile();
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { configuration } = useContext(ConfigurationContext);
  const { t: _t } = useTranslation("Change");
  const { model, id } = useParams();

  const modelConfiguration = getConfigurationModel(
    configuration,
    model as string,
  );

  const { data: initialChangeValues, isLoading: isLoadingInitialValues } =
    useQuery({
      queryKey: [`/retrieve/${model}/${id}`],
      queryFn: () => getFetcher(`/retrieve/${model}/${id}`),
      refetchOnWindowFocus: false,
    });

  const {
    mutate: mutateAdd,
    isPending: isLoadingAdd,
    isError: isErrorAdd,
  } = useMutation({
    mutationFn: (payload: any) => postFetcher(`/add/${model}`, payload),
    onSuccess: () => {
      message.success(_t("Succesfully added"));

      queryClient.invalidateQueries([`/list/${model}`] as any);
      const next = form.getFieldValue("next");
      if (next) {
        navigate(next);
      }
    },
    onError: (error: Error) => {
      handleError(error, form);
    },
  });

  const {
    mutate,
    isPending: isLoading,
    isError,
  } = useMutation({
    mutationFn: (payload: any) =>
      patchFetcher(`/change/${model}/${id}`, payload),
    onSuccess: () => {
      message.success(_t("Succesfully changed"));

      queryClient.invalidateQueries([`/retrieve/${model}/${id}`] as any);

      queryClient.invalidateQueries([`/list/${model}`] as any);
      const next = form.getFieldValue("next");
      if (next) {
        navigate(next);
      }
    },
    onError: (error: Error) => {
      handleError(error, form);
    },
  });

  const { mutate: mutateDelete } = useMutation({
    mutationFn: () => deleteFetcher(`/delete/${model}/${id}`),
    onSuccess: () => {
      message.success(_t("Successfully deleted"));

      queryClient.invalidateQueries([`/list/${model}`] as any);
      navigate(`/list/${model}`);
    },
    onError: () => {
      message.error(_t("Server error"));
    },
  });

  const onFinish = (payload: any) => {
    const saveAsNew = form.getFieldValue("save_as_new");
    if (saveAsNew) {
      mutateAdd(transformDataToServer(payload));
      return;
    }
    mutate(transformDataToServer(payload));
  };

  const onConfirmDelete = () => mutateDelete();

  const onSaveAndContinueEditing = () => {
    form.submit();
  };

  const onSaveAndAddAnother = () => {
    form.setFieldValue("next", `/add/${model}`);
    if (modelConfiguration?.save_as) {
      form.setFieldValue("save_as_new", true);
    }
    form.submit();
  };

  const onSave = () => {
    if (!modelConfiguration?.save_as_continue) {
      form.setFieldValue("next", `/list/${model}`);
    }
    form.submit();
  };

  return (
    <CrudContainer
      title={`${_t("Change")} ${
        modelConfiguration && getTitleFromModel(modelConfiguration)
      } ${id}`}
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
            { title: id },
          ]}
        />
      }
      isLoading={isLoadingInitialValues}
    >
      {initialChangeValues &&
      modelConfiguration &&
      modelConfiguration.permissions.includes(EModelPermission.Change) ? (
        <FormContainer
          modelConfiguration={modelConfiguration}
          id={id}
          form={form}
          onFinish={onFinish}
          mode="change"
          hasOperationError={isError || isErrorAdd}
          initialValues={transformDataFromServer(initialChangeValues)}
        >
          <Row gutter={[8, 8]} justify="space-between">
            <Col>
              <Space>
                <Popconfirm
                  title={_t("Are you sure?")}
                  onConfirm={onConfirmDelete}
                >
                  <Button danger={true}>
                    <DeleteOutlined /> {_t("Delete")}
                  </Button>
                </Popconfirm>
              </Space>
            </Col>
            <Col>
              <Space>
                {!isMobile && !modelConfiguration?.save_as_continue && (
                  <Button
                    loading={isLoading || isLoadingAdd}
                    onClick={onSaveAndContinueEditing}
                    type="default"
                  >
                    <SaveFilled /> {_t("Save and continue editing")}
                  </Button>
                )}
                {!isMobile && (
                  <Button
                    loading={isLoading || isLoadingAdd}
                    onClick={onSaveAndAddAnother}
                    type="default"
                  >
                    <SaveFilled />{" "}
                    {modelConfiguration?.save_as
                      ? _t("Save as new")
                      : _t("Save and add another")}
                  </Button>
                )}
                <Button
                  loading={isLoading || isLoadingAdd}
                  onClick={onSave}
                  type="primary"
                >
                  <SaveOutlined /> {_t("Save")}
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
