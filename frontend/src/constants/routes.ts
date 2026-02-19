/**
 * Centralized route paths to avoid magic strings and enable type-safe navigation.
 */
export const ROUTES = {
  HOME: "/",
  SIGN_IN: "/sign-in",
  LIST: "/list/:model",
  ADD: "/add/:model",
  CHANGE: "/change/:model/:id",
} as const;

export const buildListPath = (model: string) => `/list/${model}`;
export const buildAddPath = (model: string) => `/add/${model}`;
export const buildChangePath = (model: string, id: string | number) =>
  `/change/${model}/${id}`;
