# Manual Test Scenarios

## 1) Happy Path
- Create an employee
- Apply for a 3-day leave
- Approve it
- Check balance reflects 3 used

## 2) Invalid Dates
- end_date < start_date -> expect 400

## 3) Before Joining Date
- start_date < joining_date -> expect 400

## 4) Overlap
- Apply overlapping dates with existing PENDING/APPROVED -> expect 400

## 5) Exhaust Balance
- Apply repeatedly until 30 days used, then request more -> expect 400

## 6) Decision on Already Decided
- Approve an already approved leave -> expect 400