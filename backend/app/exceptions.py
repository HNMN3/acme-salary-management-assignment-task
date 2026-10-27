class EmployeeNotFoundError(Exception):
    def __init__(self, employee_id: int) -> None:
        super().__init__(f"Employee {employee_id} not found")
        self.employee_id = employee_id
