import { useEffect } from "react";

interface IUsePageMetaOptions {
  title?: string;
  description?: string;
  faviconHref?: string;
}

const getOrCreateMetaDescriptionTag = () => {
  let descriptionTag = document.querySelector(
    'meta[name="description"]',
  ) as HTMLMetaElement | null;

  if (!descriptionTag) {
    descriptionTag = document.createElement("meta");
    descriptionTag.name = "description";
    document.head.append(descriptionTag);
  }

  return descriptionTag;
};

const getOrCreateFaviconTag = () => {
  let faviconTag = document.querySelector(
    'link[rel="icon"]',
  ) as HTMLLinkElement | null;

  if (!faviconTag) {
    faviconTag = document.createElement("link");
    faviconTag.rel = "icon";
    document.head.append(faviconTag);
  }

  return faviconTag;
};

export const usePageMeta = ({
  title,
  description,
  faviconHref,
}: IUsePageMetaOptions) => {
  useEffect(() => {
    /* v8 ignore next -- browser-only defensive guard */
    if (typeof document === "undefined") {
      return;
    }

    if (title !== undefined) {
      document.title = title;
    }

    if (description !== undefined) {
      getOrCreateMetaDescriptionTag().setAttribute("content", description);
    }

    if (faviconHref !== undefined) {
      getOrCreateFaviconTag().setAttribute("href", faviconHref);
    }
  }, [description, faviconHref, title]);
};
