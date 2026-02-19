import axios from "axios";

const instance = axios.create({
  baseURL: window.SERVER_URL ?? "",
  withCredentials: true,
});

export const getFetcher = async (url: string): Promise<any> => {
  const { data } = await instance.get(url);
  return data;
};

export const postFetcher = async (
  url: string,
  payload: unknown,
): Promise<any> => {
  const { data } = await instance.post(url, payload);
  return data;
};

export const patchFetcher = async (
  url: string,
  payload: unknown,
): Promise<any> => {
  const { data } = await instance.patch(url, payload);
  return data;
};

export const deleteFetcher = async (url: string): Promise<void> => {
  await instance.delete(url);
};
