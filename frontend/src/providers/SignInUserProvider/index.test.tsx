import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SignInUserContext } from "./index";

const ContextReader = () => (
  <SignInUserContext.Consumer>
    {({ signedIn, signedInUser, signedInUserRefetch }) => {
      signedInUserRefetch();
      return (
        <div data-testid="default-context">
          {signedIn ? "signed-in" : "signed-out"}:
          {signedInUser ? "user" : "none"}
        </div>
      );
    }}
  </SignInUserContext.Consumer>
);

describe("SignInUserContext defaults", () => {
  it("provides signed-out defaults and callable refetch", () => {
    render(<ContextReader />);

    expect(screen.getByTestId("default-context").textContent).toBe(
      "signed-out:none",
    );
  });
});
