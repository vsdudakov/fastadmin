import { useQuery } from "@tanstack/react-query";
import React from "react";

import { getFetcher } from "@/fetchers/fetchers";

import type { IMe } from "@/interfaces/user";

interface ISignInUserContext {
  signedInUser?: IMe;
  signedInUserRefetch(): void;
  signedIn: boolean;
}

interface ISignInUserProvider {
  children?: React.ReactNode;
}

export const SignInUserContext = React.createContext<ISignInUserContext>({
  signedInUser: undefined,
  signedInUserRefetch: () => undefined,
  signedIn: false,
});
export const SignInUserConsumer = SignInUserContext.Consumer;

export const SignInUserProvider = ({ children }: ISignInUserProvider) => {
  const signedInData = useQuery({
    queryKey: ["/me"],
    queryFn: () => getFetcher("/me"),
    retry: false,
    refetchOnWindowFocus: false,
  });
  if (signedInData.isLoading) {
    return null;
  }
  const isNotAuth = !!signedInData.isError;
  return (
    <SignInUserContext.Provider
      value={{
        signedInUser: signedInData.data as IMe,
        signedInUserRefetch: signedInData.refetch,
        signedIn: !isNotAuth,
      }}
    >
      {children}
    </SignInUserContext.Provider>
  );
};
