from pydantic import BaseModel, ConfigDict


class CountrySeed(BaseModel):
    model_config = ConfigDict(frozen=True)

    code: str
    name: str
    pay_multiplier: float


class DepartmentSeed(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    base_salary: int
    roles: tuple[str, ...]


# Annual USD-equivalent pay is scaled by a per-country multiplier.
COUNTRIES: tuple[CountrySeed, ...] = (
    CountrySeed(code="US", name="United States", pay_multiplier=1.0),
    CountrySeed(code="GB", name="United Kingdom", pay_multiplier=0.85),
    CountrySeed(code="DE", name="Germany", pay_multiplier=0.9),
    CountrySeed(code="JP", name="Japan", pay_multiplier=0.8),
    CountrySeed(code="IN", name="India", pay_multiplier=0.35),
)

DEPARTMENTS: tuple[DepartmentSeed, ...] = (
    DepartmentSeed(
        name="Engineering",
        base_salary=120_000,
        roles=("Software Engineer", "QA Engineer", "DevOps Engineer"),
    ),
    DepartmentSeed(
        name="Product",
        base_salary=115_000,
        roles=("Product Manager", "Product Designer", "Business Analyst"),
    ),
    DepartmentSeed(
        name="Sales",
        base_salary=85_000,
        roles=("Account Executive", "Sales Development Rep", "Sales Engineer"),
    ),
    DepartmentSeed(
        name="Marketing",
        base_salary=80_000,
        roles=("Marketing Specialist", "Content Strategist", "Brand Manager"),
    ),
    DepartmentSeed(
        name="Finance",
        base_salary=90_000,
        roles=("Financial Analyst", "Accountant", "Controller"),
    ),
    DepartmentSeed(
        name="Legal",
        base_salary=105_000,
        roles=("Legal Counsel", "Compliance Officer", "Paralegal"),
    ),
    DepartmentSeed(
        name="Human Resources",
        base_salary=75_000,
        roles=("HR Generalist", "Recruiter", "Compensation Analyst"),
    ),
    DepartmentSeed(
        name="Operations",
        base_salary=70_000,
        roles=("Operations Analyst", "Program Manager", "Logistics Coordinator"),
    ),
)

# (title prefix, pay multiplier, selection weight, maximum bonus fraction)
LEVELS: tuple[tuple[str, float, int, float], ...] = (
    ("Junior", 0.7, 30, 0.08),
    ("", 1.0, 30, 0.10),
    ("Senior", 1.35, 25, 0.15),
    ("Lead", 1.7, 10, 0.20),
    ("Director", 2.3, 5, 0.30),
)

FIRST_NAMES: tuple[str, ...] = (
    "Aarav", "Olivia", "Liam", "Emma", "Noah", "Sophia", "Mateo", "Isabella", "Hiroshi", "Yuki",
    "Priya", "Arjun", "Hannah", "Lukas", "Mia", "Ethan", "Ava", "Oliver", "Charlotte", "James",
    "Ananya", "Rohan", "Sakura", "Kenji", "Felix", "Greta", "Daniel", "Grace", "Samuel", "Chloe",
    "Vikram", "Neha", "Jonas", "Lena", "Thomas", "Amelia", "Harry", "Ruby", "Kavya", "Takumi",
)

LAST_NAMES: tuple[str, ...] = (
    "Sharma", "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Tanaka", "Suzuki",
    "Patel", "Singh", "Mueller", "Schmidt", "Fischer", "Taylor", "Davies", "Evans", "Wilson", "Thomas",
    "Kumar", "Reddy", "Sato", "Watanabe", "Weber", "Wagner", "Anderson", "Clark", "Walker", "Hall",
    "Gupta", "Iyer", "Becker", "Hoffmann", "Roberts", "Wright", "Green", "Baker", "Nair", "Ito",
)
