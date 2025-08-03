from sqlalchemy import Column, Integer, String
from database import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(String, index=True)
    name = Column(String)
    salary = Column(Integer)
    email = Column(String, nullable=True)
    department = Column(String, nullable=True)
    location = Column(String, nullable=True)

    def to_dict(self):
        return {
            "employee_id": self.employee_id,
            "name": self.name,
            "salary": self.salary,
            "email": self.email,
            "department": self.department,
            "location": self.location,
        }