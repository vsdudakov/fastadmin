import axios from "axios";

const requestOptions = () => {
  return { withCredentials: true };
};

const instance = axios.create({
  baseURL: (window as any).SERVER_URL,
  ...requestOptions(),
});

export const getFetcher = async (url: string): Promise<any> => {
  const response = await instance.get(url);
  return response.data;
};

export const postFetcher = async (url: string, payload: any): Promise<any> => {
  const response = await instance.post(url, payload);
  return response.data;
};

export const patchFetcher = async (url: string, payload: any): Promise<any> => {
  const response = await instance.patch(url, payload);
  return response.data;
};

export const deleteFetcher = async (url: string): Promise<any> => {
  const response = await instance.delete(url);
  return response.data;
};
