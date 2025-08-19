from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date
from typing import List, Optional

from .database import Base, engine, SessionLocal
from . import models, schemas, utils

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Mini Leave Management System", version="1.0.0")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------------------- Employees ----------------------
@app.post("/employees", response_model=schemas.EmployeeOut, status_code=201)
def add_employee(payload: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    emp = models.Employee(
        name=payload.name,
        email=payload.email,
        department=payload.department,
        joining_date=payload.joining_date,
    )
    db.add(emp)
    try:
        db.commit()
        db.refresh(emp)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already exists")
    return emp

@app.get("/employees", response_model=List[schemas.EmployeeOut])
def list_employees(db: Session = Depends(get_db)):
    return db.query(models.Employee).all()

@app.get("/employees/{employee_id}", response_model=schemas.EmployeeOut)
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return emp

# ---------------------- Leave Application ----------------------
@app.post("/leaves", response_model=schemas.LeaveOut, status_code=201)
def apply_leave(payload: schemas.LeaveApply, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, payload.employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    # Validate dates
    if payload.start_date > payload.end_date:
        raise HTTPException(status_code=400, detail="Invalid dates: end_date before start_date")
    if payload.start_date < emp.joining_date:
        raise HTTPException(status_code=400, detail="Cannot apply leave before joining date")

    # Overlapping check with non-rejected leaves
    if utils.has_overlapping_request(db, emp.id, payload.start_date, payload.end_date):
        raise HTTPException(status_code=400, detail="Overlapping leave request exists")

    # Balance check (only count the year of the start_date for simplicity)
    year = utils.get_year(payload.start_date)
    approved, pending = utils.used_and_pending_days_for_year(db, emp.id, year)
    requested_days = utils.daterange_days(payload.start_date, payload.end_date)
    remaining = utils.DEFAULT_ANNUAL_LEAVE - approved  # Pending does not consume balance yet

    if requested_days > remaining:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Remaining: {remaining} days")

    lr = models.LeaveRequest(
        employee_id=emp.id,
        start_date=payload.start_date,
        end_date=payload.end_date,
        reason=payload.reason,
    )
    db.add(lr)
    db.commit()
    db.refresh(lr)
    return lr

# ---------------------- Approve / Reject ----------------------
@app.post("/leaves/{leave_id}/decision", response_model=schemas.LeaveOut)
def decide_leave(leave_id: int, payload: schemas.LeaveDecision, db: Session = Depends(get_db)):
    lr = db.get(models.LeaveRequest, leave_id)
    if not lr:
        raise HTTPException(status_code=404, detail="Leave request not found")
    if lr.status != models.LeaveStatus.PENDING:
        raise HTTPException(status_code=400, detail="Leave already decided")

    if payload.status == "APPROVED":
        # Re-check balance at decision time (state may have changed)
        year = lr.start_date.year
        approved, pending = utils.used_and_pending_days_for_year(db, lr.employee_id, year)
        requested_days = utils.daterange_days(lr.start_date, lr.end_date)
        remaining = utils.DEFAULT_ANNUAL_LEAVE - approved
        if requested_days > remaining:
            raise HTTPException(status_code=400, detail=f"Insufficient balance at approval time. Remaining: {remaining} days")
        lr.status = models.LeaveStatus.APPROVED
    else:
        lr.status = models.LeaveStatus.REJECTED

    db.add(lr)
    db.commit()
    db.refresh(lr)
    return lr

# ---------------------- Leave Balance ----------------------
@app.get("/employees/{employee_id}/leave-balance", response_model=schemas.LeaveBalanceOut)
def get_leave_balance(employee_id: int, year: Optional[int] = None, db: Session = Depends(get_db)):
    emp = db.get(models.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    yr = year or date.today().year
    approved, pending = utils.used_and_pending_days_for_year(db, employee_id, yr)
    remaining = utils.DEFAULT_ANNUAL_LEAVE - approved
    return {
        "employee_id": employee_id,
        "year": yr,
        "total_leaves": utils.DEFAULT_ANNUAL_LEAVE,
        "approved_used": approved,
        "pending": pending,
        "remaining": max(0, remaining),
    }

# ---------------------- List Leaves ----------------------
@app.get("/leaves", response_model=list[schemas.LeaveOut])
def list_leaves(employee_id: Optional[int] = None, status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(models.LeaveRequest)
    if employee_id is not None:
        q = q.filter(models.LeaveRequest.employee_id == employee_id)
    if status is not None:
        try:
            st = models.LeaveStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
        q = q.filter(models.LeaveRequest.status == st)
    return q.order_by(models.LeaveRequest.created_at.desc()).all()