# Backend 

# Project Structure
```
my-dashboard-backend/
│
├── .env                        # Environment variables (DATABASE_URL, JWT_SECRET, PORT)
├── .gitignore                  # Files/folders excluded from git (.env, __pycache__, .venv)
├── requirements.txt            # Python dependencies (fastapi, uvicorn, pydantic, sqlalchemy)
├── README.md                   # Developer setup instructions
│
└── app/                        # All application source code
    │
    ├── main.py                 # FastAPI app instantiation, mounts CORS, includes API routers
    │
    ├── config.py               # App configuration using Pydantic Settings (reads .env variables)
    ├── database.py             # Database engine setup, SessionLocal factory, and Base declarative model
    │
    ├── constants/              # Global immutable values
    │   └── enums.py            # Centralized OrderStatus, OrderType, and UserRole Python Enums
    │
    ├── middlewares/            # Global request/response processors
    │   └── logging.py          # Custom request logging for system monitoring
    │
    ├── dependencies/           # FastAPI dependency injection functions
    │   ├── auth.py             # get_current_user, get_current_active_admin (handles JWTs)
    │   └── db.py               # get_db yield function to manage transaction sessions safely
    │
    ├── utils/                  # Generic helper functions
    │   └── formatters.py       # Currency rounding, string sanitizers, date calculations
    │
    └── modules/                # Domain-driven features (The business entities)
        │
        ├── auth/               # Authentication & Login Module
        │   ├── router.py       # Endpoints: POST /auth/login, POST /auth/refresh
        │   ├── service.py      # Logic: Password hashing verification, creating JWT access tokens
        │   └── schemas.py      # Pydantic: Token, TokenData, LoginRequest models
        │
        ├── customers/          # Customer Accounts Module
        │   ├── router.py       # Endpoints: GET /customers, POST /customers
        │   ├── service.py      # Logic: Business workflows for handling customer accounts
        │   ├── repository.py   # SQL Alchemy queries: Database CRUD operations for customers
        │   ├── models.py       # Database Table Schema declaration for Customers
        │   └── schemas.py      # Pydantic: CustomerCreate, CustomerUpdate, CustomerOut models
        │
        ├── orders/             # Orders Module (Sales & Purchases Subtypes)
        │   ├── router.py       # Endpoints: GET /orders, POST /orders/sales, POST /orders/purchases
        │   ├── service.py      # Logic: Stock allocation, snapshotting prices at order time
        │   ├── repository.py   # SQLAlchemy: Joining core order tables with specific subtypes
        │   ├── models.py       # Database Table Schema definitions for Order tables
        │   └── schemas.py      # Pydantic: Complex request/response shapes for your graphs
        │
        └── transactions/       # Financial Transactions / Cashflow Ledger Module
            ├── router.py       # Endpoints: GET /transactions (implements query string filters)
            ├── service.py      # Logic: Ledger auditing, cash balance computations
            ├── repository.py   # SQLAlchemy: Fetching dynamic, filtered transaction listings
            ├── models.py       # Database Table Schema declaration for Transactions
            └── schemas.py      # Pydantic: TransactionOut, TransactionFilter models
```