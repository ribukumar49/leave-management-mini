# High Level Design (HLD)

## Architecture (MVP)
```mermaid
graph TD
  Browser[Employee/HR Browser] -->|HTTP/JSON| API[FastAPI Service]
  API --> DB[(SQLite / PostgreSQL)]
```

## Logical Data Model
```mermaid
classDiagram
  class Employee {
    +int id
    +string name
    +string email
    +string department
    +date joining_date
  }
  class LeaveRequest {
    +int id
    +int employee_id
    +date start_date
    +date end_date
    +string reason
    +enum status
    +datetime created_at
  }
  Employee "1" --> "many" LeaveRequest : has
```

## Sequence: Apply Leave
```mermaid
sequenceDiagram
  participant E as Employee
  participant API as FastAPI
  participant DB as Database
  E->>API: POST /leaves
  API->>DB: Validate employee, check overlap & balance
  DB-->>API: OK
  API-->>E: 201 Created (PENDING)
```

## Scaling Notes (50 -> 500 employees)
- Move to PostgreSQL with proper indexes: `employee.email`, `leave_requests(employee_id, status, start_date)`
- Add caching for frequent balance reads (e.g., Redis) if needed.
- Containerize (Docker), run behind a reverse proxy.
- Background jobs for reports/notifications.