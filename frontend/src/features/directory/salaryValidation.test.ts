import { describe, expect, it } from "vitest";

import { MAX_COMPENSATION, validateSalary } from "./salaryValidation";

describe("validateSalary", () => {
  it("accepts valid values", () => {
    expect(validateSalary(50_000, 0)).toEqual({});
    expect(validateSalary("50000", "1000")).toEqual({});
  });

  it("accepts the upper bound for both fields", () => {
    expect(validateSalary(MAX_COMPENSATION, MAX_COMPENSATION)).toEqual({});
  });

  it("accepts the lowest base salary of 1", () => {
    expect(validateSalary(1, 0)).toEqual({});
  });

  it("requires both fields", () => {
    expect(validateSalary("", "")).toEqual({
      baseSalary: "Base salary is required",
      bonus: "Bonus is required",
    });
  });

  it("rejects a zero or negative base salary", () => {
    expect(validateSalary(0, 0).baseSalary).toBe("Base salary must be at least $1");
    expect(validateSalary(-5, 0).baseSalary).toBe("Base salary must be at least $1");
  });

  it("rejects a negative bonus but allows zero", () => {
    expect(validateSalary(100, -1).bonus).toBe("Bonus cannot be negative");
    expect(validateSalary(100, 0).bonus).toBeUndefined();
  });

  it("rejects values above the maximum", () => {
    const errors = validateSalary(MAX_COMPENSATION + 1, MAX_COMPENSATION + 1);

    expect(errors.baseSalary).toBe("Base salary cannot exceed $10,000,000");
    expect(errors.bonus).toBe("Bonus cannot exceed $10,000,000");
  });

  it("rejects non-integer values", () => {
    expect(validateSalary(100.5, 1.5)).toEqual({
      baseSalary: "Base salary must be a whole number",
      bonus: "Bonus must be a whole number",
    });
  });

  it("reports errors per field independently", () => {
    expect(validateSalary(1000, "")).toEqual({ bonus: "Bonus is required" });
  });
});
