from dataclasses import dataclass


@dataclass(frozen=True)
class CountrySeed:
    code: str
    name: str
    pay_multiplier: float


@dataclass(frozen=True)
class DepartmentSeed:
    name: str
    base_salary: int
    roles: tuple[str, ...]


# Annual USD-equivalent pay is scaled by a per-country multiplier.
COUNTRIES: tuple[CountrySeed, ...] = (
    CountrySeed("US", "United States", 1.0),
    CountrySeed("GB", "United Kingdom", 0.85),
    CountrySeed("DE", "Germany", 0.9),
    CountrySeed("JP", "Japan", 0.8),
    CountrySeed("IN", "India", 0.35),
)

DEPARTMENTS: tuple[DepartmentSeed, ...] = (
    DepartmentSeed("Engineering", 120_000, ("Software Engineer", "QA Engineer", "DevOps Engineer")),
    DepartmentSeed("Product", 115_000, ("Product Manager", "Product Designer", "Business Analyst")),
    DepartmentSeed("Sales", 85_000, ("Account Executive", "Sales Development Rep", "Sales Engineer")),
    DepartmentSeed("Marketing", 80_000, ("Marketing Specialist", "Content Strategist", "Brand Manager")),
    DepartmentSeed("Finance", 90_000, ("Financial Analyst", "Accountant", "Controller")),
    DepartmentSeed("Legal", 105_000, ("Legal Counsel", "Compliance Officer", "Paralegal")),
    DepartmentSeed("Human Resources", 75_000, ("HR Generalist", "Recruiter", "Compensation Analyst")),
    DepartmentSeed("Operations", 70_000, ("Operations Analyst", "Program Manager", "Logistics Coordinator")),
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
