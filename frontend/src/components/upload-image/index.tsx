import { UploadOutlined } from "@ant-design/icons";
import type { UploadFile } from "antd";
import { Image, Modal, Space, Upload } from "antd";
import ImgCrop from "antd-img-crop";
import getBase64 from "getbase64data";
import type React from "react";
import { useContext, useMemo, useState } from "react";
import { useTranslation } from "react-i18next";

import { ConfigurationContext } from "@/providers/ConfigurationProvider";

const UploadWrapper: React.FC<{
  withCrop?: boolean;
  children: React.ReactElement;
}> = ({ withCrop, children }) =>
  withCrop ? <ImgCrop rotationSlider>{children}</ImgCrop> : children;

const serverDomain = window.SERVER_DOMAIN ?? "";
const serverUrl = window.SERVER_URL ?? "";

export interface IUploadImage {
  model: string;
  fieldName: string;
  value?: string;
  onChange?: (value: string | undefined) => void;
  disableCropImage?: boolean;
}

export const UploadImage: React.FC<IUploadImage> = ({
  value,
  onChange,
  disableCropImage,
  model,
  fieldName,
  ...rest
}) => {
  const { t: _t } = useTranslation("UploadInput");
  const [previewUrl, setPreviewUrl] = useState<string | undefined>();
  const { configuration } = useContext(ConfigurationContext);

  const defaultFileList = useMemo((): UploadFile[] | undefined => {
    if (!value) return undefined;
    const url = value.startsWith("http") ? value : `${serverDomain}${value}`;
    return [
      {
        uid: "0",
        name: value.split("/").pop() ?? value,
        status: "done",
        url,
      },
    ];
  }, [value]);

  const handleChange = (info: { fileList: UploadFile[] }) => {
    const file = info.fileList[0];
    if (!file) {
      onChange?.(undefined);
      return;
    }
    if (file.status === "done") {
      const path =
        typeof file.response === "string"
          ? file.response
          : (file.response as { url?: string })?.url;
      if (path) onChange?.(path);
    }
  };

  const onPreview = async (file: UploadFile) => {
    if (file.url) {
      setPreviewUrl(file.url);
      return;
    }
    if (file.originFileObj) {
      setPreviewUrl(await getBase64.fromFile(file.originFileObj));
    }
  };

  const action =
    model && fieldName
      ? `${serverUrl}/upload-file/${model}/${fieldName}`
      : undefined;

  return (
    <>
      <UploadWrapper
        withCrop={!configuration?.disable_crop_image && !disableCropImage}
      >
        <Upload
          {...rest}
          listType="picture-card"
          withCredentials
          action={action}
          onChange={handleChange}
          defaultFileList={defaultFileList}
          multiple={false}
          onPreview={onPreview}
          accept="image/*"
          maxCount={1}
        >
          <Space>
            <UploadOutlined />
            {_t("Upload")}
          </Space>
        </Upload>
      </UploadWrapper>
      <Modal
        footer={null}
        title={_t("Preview Image")}
        open={!!previewUrl}
        onCancel={() => setPreviewUrl(undefined)}
      >
        <Image preview={false} src={previewUrl} />
      </Modal>
    </>
  );
};
