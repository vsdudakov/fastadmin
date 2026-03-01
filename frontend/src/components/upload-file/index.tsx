import { UploadOutlined } from "@ant-design/icons";
import type { UploadFile as AntUploadFile } from "antd";
import { Button, Upload } from "antd";
import type React from "react";
import { useMemo } from "react";
import { useTranslation } from "react-i18next";

const serverDomain = window.SERVER_DOMAIN ?? "";
const serverUrl = window.SERVER_URL ?? "";

export type UploadFileValue = string | undefined;

export interface IUploadFileProps {
  parentId: string;
  model?: string;
  fieldName?: string;
  value?: UploadFileValue;
  onChange?: (value: UploadFileValue) => void;
  accept?: string;
}

const norm = (v: UploadFileValue): string[] => (!v ? [] : [v]);

export const UploadFile: React.FC<IUploadFileProps> = ({
  value,
  onChange,
  accept,
  parentId,
  model,
  fieldName,
  ...rest
}) => {
  const { t: _t } = useTranslation("UploadInput");

  const defaultFileList = useMemo((): AntUploadFile[] | undefined => {
    const paths = norm(value);
    if (paths.length === 0) return undefined;
    return paths.map((path, index) => ({
      uid: `existing-${index}-${path}`,
      name: path.split("/").pop() ?? path,
      status: "done" as const,
      url: path.startsWith("http") ? path : `${serverDomain}${path}`,
    }));
  }, [value]);

  const handleChange = (info: { fileList: AntUploadFile[] }) => {
    if (!onChange) return;
    const list = info.fileList;
    if (list.length === 0) {
      onChange(undefined);
      return;
    }
    const paths: string[] = [];
    for (const f of list) {
      if (f.status === "done") {
        const path =
          typeof f.response === "string"
            ? f.response
            : (f.response as { url?: string })?.url;
        if (path) paths.push(path);
        else if (f.url)
          paths.push(
            f.url.startsWith(serverDomain)
              ? f.url.slice(serverDomain.length)
              : f.url,
          );
      }
    }
    if (paths.length > 0) onChange(paths[0]);
  };

  const action =
    model && fieldName
      ? `${serverUrl}/upload-file/${model}/${parentId}/${fieldName}`
      : undefined;

  return (
    <Upload
      {...rest}
      listType="picture"
      withCredentials
      action={action}
      onChange={handleChange}
      defaultFileList={defaultFileList}
      multiple={false}
      accept={accept}
      maxCount={1}
    >
      <Button icon={<UploadOutlined />} type="primary">
        {_t("Upload")}
      </Button>
    </Upload>
  );
};
