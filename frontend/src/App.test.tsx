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
      vi.fn(async (url: string) =>
        String(url).endsWith("/health")
          ? { ok: true, json: async () => ({ status: "ok" }) }
          : { ok: false, status: 500, statusText: "Error", json: async () => ({}) },
      ),
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
    expect(screen.getByLabelText("Search")).toBeInTheDocument();

    await userEvent.click(screen.getByRole("tab", { name: "Analytics" }));

    expect(screen.getByText("Analytics dashboard")).toBeInTheDocument();
    expect(screen.queryByLabelText("Search")).not.toBeInTheDocument();
  });
});
