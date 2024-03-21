import { PlusCircleOutlined, SaveOutlined } from "@ant-design/icons";
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
import { getFetcher, postFetcher } from "@/fetchers/fetchers";
import { handleError } from "@/helpers/forms";
import { getTitleFromModel } from "@/helpers/title";
import { EModelPermission, type IModel } from "@/interfaces/configuration";
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
  const { t: _t } = useTranslation("AsyncSelect");
  const [search, setSearch] = useState<string | undefined>();
  const [openAdd, setOpenAdd] = useState<boolean>(false);
  const { configuration } = useContext(ConfigurationContext);
  const modelConfiguration: IModel | undefined = configuration.models.find(
    (item: IModel) => item.name === parentModel,
  );

  const queryString = querystring.stringify({
    offset: 0,
    limit: 20,
    search,
  });

  const { data, isLoading, refetch } = useQuery({
    queryKey: [`/list/${parentModel}`, queryString],
    queryFn: () => getFetcher(`/list/${parentModel}?${queryString}`),
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

  return (
    <>
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
        <Select
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
          value={value ? `${value}` : undefined}
          {...props}
        />
      </Space.Compact>
    </>
  );
};
