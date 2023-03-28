import React, { useCallback, useContext, useState } from 'react';
import {
  Button,
  Col,
  Divider,
  Empty,
  Form,
  message,
  Modal,
  Row,
  Select,
  Space,
  Tooltip,
} from 'antd';
import { useMutation, useQuery } from '@tanstack/react-query';
import { PlusCircleOutlined, SaveOutlined } from '@ant-design/icons';
import debounce from 'lodash.debounce';
import querystring from 'querystring';
import { useTranslation } from 'react-i18next';

import { getFetcher, postFetcher } from 'fetchers/fetchers';
import { FormContainer } from 'components/form-container';
import { handleError } from 'helpers/forms';
import { getTitleFromModelClass } from 'helpers/title';
import { EModelPermission, IModel } from 'interfaces/configuration';
import { ConfigurationContext } from 'providers/ConfigurationProvider';

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
  const { t: _t } = useTranslation('AsyncSelect');
  const [search, setSearch] = useState<string | undefined>();
  const [openAdd, setOpenAdd] = useState<boolean>(false);
  const { configuration } = useContext(ConfigurationContext);
  const modelConfiguration: IModel | undefined = configuration.models.find(
    (item: IModel) => item.name === parentModel
  );

  const queryString = querystring.stringify({
    offset: 0,
    limit: 20,
    search,
  });

  const { data, isLoading, refetch } = useQuery([`/list/${parentModel}`, queryString], () =>
    getFetcher(`/list/${parentModel}?${queryString}`)
  );

  const {
    mutate: mutateAdd,
    isLoading: isLoadingAdd,
    isError: isErrorAdd,
  } = useMutation((payload: any) => postFetcher(`/add/${parentModel}`, payload), {
    onSuccess: () => {
      message.success(_t('Succesfully added'));
      refetch();
      onCloseAdd();
    },
    onError: (error: Error) => {
      handleError(error, formAdd);
    },
  });

  const onFilter = (input: string, option: any) => {
    return (
      ((option?.label as any) || '').toString().toLowerCase().indexOf(input.toLowerCase()) >= 0 ||
      ((option?.value as any) || '').toString().toLowerCase().indexOf(input.toLowerCase()) >= 0
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
        title={_t(`Add ${getTitleFromModelClass(parentModel)}`)}
        onCancel={onCloseAdd}
        footer={null}
      >
        <Divider />
        {modelConfiguration && modelConfiguration.permissions.includes(EModelPermission.Add) ? (
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
                  <Button loading={isLoadingAdd} htmlType="submit" type="primary">
                    <SaveOutlined /> {_t('Add')}
                  </Button>
                </Space>
              </Col>
            </Row>
          </FormContainer>
        ) : (
          <Empty description={_t('No permissions for model')} />
        )}
      </Modal>
      <Space.Compact style={{ width: '100%' }}>
        <Tooltip title={_t(`Add ${getTitleFromModelClass(parentModel)}`)}>
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
