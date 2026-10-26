import { screen } from "@testing-library/react";
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
});
