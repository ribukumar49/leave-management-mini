from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, Literal

class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    department: str = Field(..., min_length=1)
    joining_date: date

class EmployeeOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    department: str
    joining_date: date

    class Config:
        from_attributes = True

class LeaveApply(BaseModel):
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None

class LeaveDecision(BaseModel):
    status: Literal["APPROVED", "REJECTED"]

class LeaveOut(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    reason: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

class LeaveBalanceOut(BaseModel):
    employee_id: int
    year: int
    total_leaves: int
    approved_used: int
    pending: int
    remaining: int