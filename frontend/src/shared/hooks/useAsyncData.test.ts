import { act, renderHook, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { useAsyncData } from "./useAsyncData";

describe("useAsyncData", () => {
  it("starts loading and then exposes the data", async () => {
    const load = vi.fn().mockResolvedValue("result");

    const { result } = renderHook(() => useAsyncData(load, []));

    expect(result.current.loading).toBe(true);
    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.data).toBe("result");
    expect(result.current.error).toBeUndefined();
  });

  it("exposes the error when loading fails", async () => {
    const load = vi.fn().mockRejectedValue(new Error("boom"));

    const { result } = renderHook(() => useAsyncData(load, []));

    await waitFor(() => expect(result.current.loading).toBe(false));
    expect(result.current.error?.message).toBe("boom");
    expect(result.current.data).toBeUndefined();
  });

  it("reloads when a dependency changes", async () => {
    const load = vi.fn().mockResolvedValueOnce("first").mockResolvedValueOnce("second");

    const { result, rerender } = renderHook(
      ({ dep }) => useAsyncData(load, [dep]),
      { initialProps: { dep: 1 } },
    );
    await waitFor(() => expect(result.current.data).toBe("first"));

    rerender({ dep: 2 });

    await waitFor(() => expect(result.current.data).toBe("second"));
    expect(load).toHaveBeenCalledTimes(2);
  });

  it("reloads when reload is called", async () => {
    const load = vi.fn().mockResolvedValueOnce("first").mockResolvedValueOnce("second");

    const { result } = renderHook(() => useAsyncData(load, []));
    await waitFor(() => expect(result.current.data).toBe("first"));

    act(() => result.current.reload());

    await waitFor(() => expect(result.current.data).toBe("second"));
  });

  it("ignores a stale response that resolves after a newer request", async () => {
    let resolveFirst!: (value: string) => void;
    const load = vi
      .fn()
      .mockImplementationOnce(
        () => new Promise<string>((resolve) => (resolveFirst = resolve)),
      )
      .mockResolvedValueOnce("second");

    const { result, rerender } = renderHook(
      ({ dep }) => useAsyncData(load, [dep]),
      { initialProps: { dep: 1 } },
    );
    rerender({ dep: 2 });
    await waitFor(() => expect(result.current.data).toBe("second"));

    await act(async () => resolveFirst("first"));

    expect(result.current.data).toBe("second");
  });
});
