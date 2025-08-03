from pydantic import BaseModel
from typing import Optional

class UnifiedEmployee(BaseModel):
    employee_id: str
    name: str
    salary: Optional[float] = None
    email: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None

