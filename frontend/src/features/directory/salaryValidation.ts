import { formatCurrency } from "../../shared/format";

export const MAX_COMPENSATION = 10_000_000;

export interface SalaryErrors {
  baseSalary?: string;
  bonus?: string;
}

type FieldValue = number | string;

function validateAmount(
  label: string,
  value: FieldValue,
  minimum: number,
): string | undefined {
  if (value === "") {
    return `${label} is required`;
  }
  const amount = Number(value);
  if (!Number.isInteger(amount)) {
    return `${label} must be a whole number`;
  }
  if (amount < minimum) {
    return minimum > 0
      ? `${label} must be at least ${formatCurrency(minimum)}`
      : `${label} cannot be negative`;
  }
  if (amount > MAX_COMPENSATION) {
    return `${label} cannot exceed ${formatCurrency(MAX_COMPENSATION)}`;
  }
  return undefined;
}

export function validateSalary(
  baseSalary: FieldValue,
  bonus: FieldValue,
): SalaryErrors {
  const errors: SalaryErrors = {};
  const baseError = validateAmount("Base salary", baseSalary, 1);
  const bonusError = validateAmount("Bonus", bonus, 0);
  if (baseError) errors.baseSalary = baseError;
  if (bonusError) errors.bonus = bonusError;
  return errors;
}
