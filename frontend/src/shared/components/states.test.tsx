import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { renderWithProviders } from "../../test/renderWithProviders";
import { ErrorState } from "./ErrorState";
import { LoadingState } from "./LoadingState";

describe("LoadingState", () => {
  it("exposes an accessible status", () => {
    renderWithProviders(<LoadingState label="Loading employees" />);

    expect(screen.getByRole("status", { name: "Loading employees" })).toBeInTheDocument();
  });
});

describe("ErrorState", () => {
  it("shows the message without a retry button by default", () => {
    renderWithProviders(<ErrorState message="Request failed" />);

    expect(screen.getByText("Request failed")).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Retry" })).not.toBeInTheDocument();
  });

  it("calls onRetry when the retry button is clicked", async () => {
    const onRetry = vi.fn();
    renderWithProviders(<ErrorState message="Request failed" onRetry={onRetry} />);

    await userEvent.click(screen.getByRole("button", { name: "Retry" }));

    expect(onRetry).toHaveBeenCalledOnce();
  });
});
