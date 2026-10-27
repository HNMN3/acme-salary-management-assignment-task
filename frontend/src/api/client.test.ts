import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, apiGet, apiPatch, buildQueryString } from "./client";

function stubFetch(response: Partial<Response> & { json?: () => Promise<unknown> }) {
  const fetchMock = vi.fn().mockResolvedValue(response);
  vi.stubGlobal("fetch", fetchMock);
  return fetchMock;
}

describe("buildQueryString", () => {
  it("skips empty values and keeps zero", () => {
    expect(
      buildQueryString({ a: 1, b: undefined, c: null, d: "", e: 0, f: "x y" }),
    ).toBe("?a=1&e=0&f=x+y");
  });

  it("returns an empty string without parameters", () => {
    expect(buildQueryString()).toBe("");
    expect(buildQueryString({ a: undefined })).toBe("");
  });
});

describe("api client", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("appends query parameters to GET requests", async () => {
    const fetchMock = stubFetch({ ok: true, json: async () => [] });

    await apiGet("/employees", { page: 2, search: undefined });

    expect(fetchMock.mock.calls[0][0]).toMatch(/\/employees\?page=2$/);
  });

  it("sends PATCH requests as JSON", async () => {
    const fetchMock = stubFetch({ ok: true, json: async () => ({ id: 1 }) });

    await apiPatch("/employees/1/salary", { base_salary: 10, bonus: 0 });

    const [, init] = fetchMock.mock.calls[0];
    expect(init.method).toBe("PATCH");
    expect(init.headers).toEqual({ "Content-Type": "application/json" });
    expect(JSON.parse(init.body)).toEqual({ base_salary: 10, bonus: 0 });
  });

  it("throws an ApiError carrying the server's detail message", async () => {
    stubFetch({
      ok: false,
      status: 404,
      statusText: "Not Found",
      json: async () => ({ detail: "Employee 9 not found" }),
    });

    await expect(apiGet("/employees")).rejects.toMatchObject({
      status: 404,
      message: "Employee 9 not found",
    });
  });

  it("uses the first validation message for 422 responses", async () => {
    stubFetch({
      ok: false,
      status: 422,
      statusText: "Unprocessable Entity",
      json: async () => ({ detail: [{ msg: "Input should be greater than 0" }] }),
    });

    await expect(apiPatch("/x", {})).rejects.toThrow(
      "Input should be greater than 0",
    );
  });

  it("falls back to the status text when the body is not JSON", async () => {
    stubFetch({
      ok: false,
      status: 500,
      statusText: "Internal Server Error",
      json: async () => {
        throw new Error("not json");
      },
    });

    const error = await apiGet("/employees").catch((e: unknown) => e);

    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).message).toBe("Internal Server Error");
  });
});
