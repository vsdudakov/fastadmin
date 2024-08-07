import {
  EditOutlined,
  PlusCircleOutlined,
  SaveOutlined,
} from "@ant-design/icons";
import { useMutation, useQuery } from "@tanstack/react-query";
import {
  Button,
  Col,
  Divider,
  Empty,
  Form,
  Modal,
  Row,
  Select,
  Space,
  Tooltip,
  message,
} from "antd";
import debounce from "lodash.debounce";
import querystring from "query-string";
import type React from "react";
import { useCallback, useContext, useState } from "react";
import { useTranslation } from "react-i18next";

import { FormContainer } from "@/components/form-container";
import { getFetcher, patchFetcher, postFetcher } from "@/fetchers/fetchers";
import { getConfigurationModel } from "@/helpers/configuration";
import { handleError } from "@/helpers/forms";
import { getTitleFromModel } from "@/helpers/title";
import { transformDataFromServer } from "@/helpers/transform";
import { EModelPermission } from "@/interfaces/configuration";
import { ConfigurationContext } from "@/providers/ConfigurationProvider";

export interface IAsyncSelect {
  idField: string;
  labelFields: string[];

  value?: any;
  parentModel: string;
}

export const AsyncSelect: React.FC<IAsyncSelect> = ({
  idField,
  labelFields,
  value,
  parentModel,
  ...props
}) => {
  const [formAdd] = Form.useForm();
  const [formChange] = Form.useForm();
  const { t: _t } = useTranslation("AsyncSelect");
  const [search, setSearch] = useState<string | undefined>();

  const { configuration } = useContext(ConfigurationContext);

  const [openAdd, setOpenAdd] = useState<boolean>(false);
  const [openChange, setOpenChange] = useState<any | undefined>();

  const modelConfiguration = getConfigurationModel(configuration, parentModel);

  const queryString = querystring.stringify({
    offset: 0,
    limit: 20,
    search,
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: [`/list/${parentModel}`, queryString],
    queryFn: () => getFetcher(`/list/${parentModel}?${queryString}`),
  });

  const { data: initialChangeValues, isLoading: isLoadingInitialValues } =
    useQuery({
      queryKey: [`/retrieve/${parentModel}/${openChange}`],
      queryFn: () => getFetcher(`/retrieve/${parentModel}/${openChange}`),
      enabled: !!openChange,
      refetchOnWindowFocus: false,
    });

  const {
    mutate: mutateAdd,
    isPending: isLoadingAdd,
    isError: isErrorAdd,
  } = useMutation({
    mutationFn: (payload: any) => postFetcher(`/add/${parentModel}`, payload),
    onSuccess: () => {
      message.success(_t("Succesfully added"));
      refetch();
      onCloseAdd();
    },
    onError: (error: Error) => {
      handleError(error, formAdd);
    },
  });

  const {
    mutate: mutateChange,
    isPending: isLoadingChange,
    isError: isErrorChange,
  } = useMutation({
    mutationFn: (data: any) =>
      patchFetcher(`/change/${parentModel}/${openChange}`, data),
    onSuccess: () => {
      message.success(_t("Succesfully changed"));
      refetch();
      onCloseChange();
    },
    onError: (error: Error) => {
      handleError(error, formChange);
    },
  });

  const onFilter = (input: string, option: any) => {
    return (
      ((option?.label as any) || "")
        .toString()
        .toLowerCase()
        .indexOf(input.toLowerCase()) >= 0 ||
      ((option?.value as any) || "")
        .toString()
        .toLowerCase()
        .indexOf(input.toLowerCase()) >= 0
    );
  };

  const onSearch = (v: string) => {
    setSearch(v);
  };

  const onOpenAdd = useCallback(() => {
    formAdd.resetFields();
    setOpenAdd(true);
  }, [formAdd]);

  const onCloseAdd = useCallback(() => {
    setOpenAdd(false);
  }, []);

  const onFinishAdd = (payload: any) => {
    mutateAdd(payload);
  };

  const onOpenChange = useCallback(
    (itemId: string) => {
      formChange.resetFields();
      setOpenChange(itemId);
      setOpenAdd(false);
    },
    [formChange],
  );

  const onCloseChange = useCallback(() => {
    setOpenChange(undefined);
    setOpenAdd(false);
  }, []);

  const onFinishChange = (payload: any) => {
    mutateChange(payload);
  };

  const isMultipleMode = (props as any).mode === "multiple";

  return (
    <>
      <Space.Compact style={{ width: "100%" }}>
        <Tooltip
          title={_t(
            `Add ${
              modelConfiguration && getTitleFromModel(modelConfiguration)
            }`,
          )}
        >
          <Button onClick={onOpenAdd}>
            <PlusCircleOutlined />
          </Button>
        </Tooltip>
        {value && !isMultipleMode && (
          <Tooltip
            title={_t(
              `Edit ${
                modelConfiguration && getTitleFromModel(modelConfiguration)
              }`,
            )}
          >
            <Button onClick={() => onOpenChange(value)}>
              <EditOutlined />
            </Button>
          </Tooltip>
        )}
        <Select
          allowClear={true}
          showSearch={true}
          loading={isLoading}
          filterOption={onFilter}
          onSearch={debounce(onSearch, 500)}
          options={(data?.results || []).map((item: any) => {
            const labelField = labelFields.filter((f) => item[f])[0];
            return {
              value: `${item[idField]}`,
              label: item[labelField],
            };
          })}
          value={
            isMultipleMode
              ? value
                ? value.map((v: any) => `${v}`)
                : []
              : value
                ? `${value}`
                : undefined
          }
          {...props}
        />
      </Space.Compact>
      <Modal
        width={600}
        open={openAdd}
        title={_t(
          `Add ${modelConfiguration && getTitleFromModel(modelConfiguration)}`,
        )}
        onCancel={onCloseAdd}
        footer={null}
      >
        <Divider />
        {modelConfiguration?.permissions.includes(EModelPermission.Add) ? (
          <FormContainer
            modelConfiguration={modelConfiguration}
            form={formAdd}
            onFinish={onFinishAdd}
            mode="inline-add"
            hasOperationError={isErrorAdd}
          >
            <Row justify="end">
              <Col>
                <Space>
                  <Button
                    loading={isLoadingAdd}
                    htmlType="submit"
                    type="primary"
                  >
                    <SaveOutlined /> {_t("Add")}
                  </Button>
                </Space>
              </Col>
            </Row>
          </FormContainer>
        ) : (
          <Empty description={_t("No permissions for model")} />
        )}
      </Modal>
      <Modal
        width={600}
        open={!!openChange}
        title={`Change ${modelConfiguration && getTitleFromModel(modelConfiguration)} ${openChange}`}
        onCancel={onCloseChange}
        footer={null}
      >
        <Divider />
        {initialChangeValues &&
        modelConfiguration &&
        modelConfiguration.permissions.includes(EModelPermission.Change) ? (
          <FormContainer
            modelConfiguration={modelConfiguration}
            form={formChange}
            onFinish={onFinishChange}
            mode="inline-change"
            hasOperationError={isErrorChange}
            initialValues={transformDataFromServer(initialChangeValues)}
          >
            <Row justify="end">
              <Col>
                <Space>
                  <Button
                    loading={isLoadingChange || isLoadingInitialValues}
                    htmlType="submit"
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
      </Modal>
    </>
  );
};
