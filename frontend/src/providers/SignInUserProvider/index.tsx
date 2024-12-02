import React from "react";

import type { IMe } from "@/interfaces/user";

interface ISignInUserContext {
  signedInUser?: IMe;
  signedInUserRefetch(): void;
  signedIn: boolean;
}

export const SignInUserContext = React.createContext<ISignInUserContext>({
  signedInUser: undefined,
  signedInUserRefetch: () => undefined,
  signedIn: false,
});
