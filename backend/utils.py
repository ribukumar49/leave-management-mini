from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
from .models import LeaveRequest, LeaveStatus

# Business rules
DEFAULT_ANNUAL_LEAVE = 30

def daterange_days(start: date, end: date) -> int:
    """Inclusive calendar days between start and end."""
    return (end - start).days + 1

def overlaps(a_start: date, a_end: date, b_start: date, b_end: date) -> bool:
    return not (a_end < b_start or b_end < a_start)

def get_year(d: date) -> int:
    return d.year

def used_and_pending_days_for_year(db: Session, employee_id: int, year: int) -> tuple[int, int]:
    """Return (approved_days, pending_days) in a given year for an employee."""
    # We count any leave whose range intersects the year window
    y_start = date(year, 1, 1)
    y_end = date(year, 12, 31)

    stmt = select(LeaveRequest).where(
        and_(
            LeaveRequest.employee_id == employee_id,
            # overlap with [y_start, y_end]
            or_(
                and_(LeaveRequest.start_date <= y_end, LeaveRequest.end_date >= y_start),
            )
        )
    )
    approved = 0
    pending = 0
    for lr in db.scalars(stmt):
        # Clip to the year window
        start = max(lr.start_date, y_start)
        end = min(lr.end_date, y_end)
        days = daterange_days(start, end)
        if lr.status == LeaveStatus.APPROVED:
            approved += days
        elif lr.status == LeaveStatus.PENDING:
            pending += days
    return approved, pending

def has_overlapping_request(db: Session, employee_id: int, start: date, end: date) -> bool:
    """Check if there is an existing non-rejected request that overlaps this range."""
    stmt = select(LeaveRequest).where(
        and_(
            LeaveRequest.employee_id == employee_id,
            LeaveRequest.status != LeaveStatus.REJECTED,
            LeaveRequest.start_date <= end,
            LeaveRequest.end_date >= start,
        )
    )
    return db.scalars(stmt).first() is not None