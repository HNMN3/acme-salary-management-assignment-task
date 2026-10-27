import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import { renderWithProviders } from "./test/renderWithProviders";

describe("App", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the backend as online when the health check succeeds", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ status: "ok" }),
      }),
    );

    renderWithProviders(<App />);

    expect(await screen.findByText("Backend online")).toBeInTheDocument();
  });

  it("shows the backend as offline when the health check fails", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network")));

    renderWithProviders(<App />);

    expect(await screen.findByText("Backend offline")).toBeInTheDocument();
  });

  it("switches between the Directory and Analytics tabs", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("network")));

    renderWithProviders(<App />);

    expect(screen.getByRole("tab", { name: "Directory" })).toHaveAttribute(
      "aria-selected",
      "true",
    );
    expect(screen.getByText("Employee directory")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("tab", { name: "Analytics" }));

    expect(screen.getByText("Analytics dashboard")).toBeInTheDocument();
    expect(screen.queryByText("Employee directory")).not.toBeInTheDocument();
  });
});
