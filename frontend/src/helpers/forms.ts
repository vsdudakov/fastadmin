import { message } from "antd";
import type { FormInstance } from "rc-field-form";

export const handleError = (error: any, form?: FormInstance) => {
  const errors =
    error?.response?.data?.detail || error?.response?.data?.description;
  if (!Array.isArray(errors)) {
    if (typeof errors === "string" || errors instanceof String) {
      message.error(errors);
    } else {
      message.error("Server error");
    }
    return;
  }

  const errorsData: any = {};
  for (const item of errors) {
    const fieldArray = item?.loc || [];
    const field = fieldArray[fieldArray.length - 1];
    if (!field || !item?.msg) {
      continue;
    }
    errorsData[field] = [item?.msg];
  }

  if (!form) {
    message.error("Server error");
    return;
  }

  const errorsFields: any = [];
  const fields = Object.keys(form.getFieldsValue()).filter(
    (key) => key in errorsData,
  );
  for (const field of fields) {
    errorsFields.push({
      name: field,
      errors: errorsData[field],
    });
  }

  if (errorsFields.length > 0) {
    form.setFields(errorsFields);
  }
};

export const cleanFormErrors = (form: FormInstance) => {
  const errorsFields: any = [];
  const fields = Object.keys(form.getFieldsValue());

  for (const field of fields) {
    errorsFields.push({
      name: field,
      errors: [],
    });
  }

  form.setFields(errorsFields);
};
