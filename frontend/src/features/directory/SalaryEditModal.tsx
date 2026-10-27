import { Alert, Button, Group, Modal, NumberInput, Stack, Text } from "@mantine/core";
import { useState } from "react";
import type { FormEvent } from "react";

import { updateSalary } from "../../api/employees";
import type { Employee } from "../../api/types";
import { formatCurrency } from "../../shared/format";
import { validateSalary } from "./salaryValidation";
import type { SalaryErrors } from "./salaryValidation";

interface SalaryEditModalProps {
  employee: Employee | null;
  onClose: () => void;
  onSaved: (employee: Employee) => void;
}

export function SalaryEditModal({
  employee,
  onClose,
  onSaved,
}: SalaryEditModalProps) {
  return (
    <Modal opened={employee !== null} onClose={onClose} title="Edit salary">
      {employee && (
        <SalaryForm
          key={employee.id}
          employee={employee}
          onClose={onClose}
          onSaved={onSaved}
        />
      )}
    </Modal>
  );
}

interface SalaryFormProps {
  employee: Employee;
  onClose: () => void;
  onSaved: (employee: Employee) => void;
}

function SalaryForm({ employee, onClose, onSaved }: SalaryFormProps) {
  const [baseSalary, setBaseSalary] = useState<number | string>(employee.base_salary);
  const [bonus, setBonus] = useState<number | string>(employee.bonus);
  const [errors, setErrors] = useState<SalaryErrors>({});
  const [submitError, setSubmitError] = useState<string>();
  const [saving, setSaving] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const validation = validateSalary(baseSalary, bonus);
    setErrors(validation);
    if (validation.baseSalary || validation.bonus) {
      return;
    }

    setSaving(true);
    setSubmitError(undefined);
    try {
      const updated = await updateSalary(employee.id, {
        base_salary: Number(baseSalary),
        bonus: Number(bonus),
      });
      onSaved(updated);
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : "Update failed");
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <Stack>
        <div>
          <Text fw={600}>
            {employee.first_name} {employee.last_name}
          </Text>
          <Text size="sm" c="dimmed">
            {employee.job_title} · {employee.country.name}
          </Text>
        </div>
        <NumberInput
          label="Base salary"
          prefix="$"
          thousandSeparator=","
          allowDecimal={false}
          allowNegative={false}
          hideControls
          value={baseSalary}
          onChange={setBaseSalary}
          error={errors.baseSalary}
          data-autofocus
        />
        <NumberInput
          label="Bonus"
          prefix="$"
          thousandSeparator=","
          allowDecimal={false}
          allowNegative={false}
          hideControls
          value={bonus}
          onChange={setBonus}
          error={errors.bonus}
        />
        <Text size="sm" c="dimmed">
          Total compensation:{" "}
          {formatCurrency((Number(baseSalary) || 0) + (Number(bonus) || 0))}
        </Text>
        {submitError && (
          <Alert color="red" role="alert">
            {submitError}
          </Alert>
        )}
        <Group justify="flex-end">
          <Button variant="default" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button type="submit" loading={saving}>
            Save
          </Button>
        </Group>
      </Stack>
    </form>
  );
}
