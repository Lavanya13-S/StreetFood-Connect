# StreetConnect Platform

StreetConnect is a full-stack web application that connects street food vendors with trusted suppliers. The platform provides dashboards for both vendors and suppliers, product management, order processing, analytics, and more.

## Project Structure

- `backend/` — FastAPI backend (Python)
- `frontend/` — React frontend (JavaScript)
- `tests/` — Backend test scripts

## Features
- Vendor and supplier registration/login
- Product browsing, search, and management
- Order placement and management
- Analytics dashboards
- PDF invoice generation
- Secure authentication (JWT)
- Responsive, modern UI

## Prerequisites
- Python 3.8+
- Node.js (v16 or higher recommended)
- npm (comes with Node.js)
- MongoDB (local or remote instance)

## Getting Started

### 1. Clone the repository

```
git clone <repo-url>
cd vendor_cloned_app_corrected
```

### 2. Backend Setup

```
cd backend
pip install -r requirements.txt
```

- Create a `.env` file in `backend/` with:
  ```
  MONGO_URL="mongodb://localhost:27017"
  DB_NAME="test_database"
  SECRET_KEY="your-secret-key"
  ```
- Start the backend server:
  ```
  python server.py
  ```
  The backend runs at [http://localhost:8000](http://localhost:8000)

### 3. Frontend Setup

```
cd ../frontend
npm install
```
- Create a `.env` file in `frontend/` with:
  ```
  REACT_APP_BACKEND_URL=http://localhost:8000
  ```
- Start the frontend:
  ```
  npm start
  ```
  The frontend runs at [http://localhost:3000](http://localhost:3000)

### 4. Running Tests
- Backend tests are in the `tests/` directory.
- Run with:
  ```
  python -m unittest discover ../tests
  ```

## Usage
- Register as a vendor or supplier.
- Vendors can browse products, place orders, and view analytics.
- Suppliers can manage products, view orders, and see analytics.

## Troubleshooting
- If you see 400/401 errors, check that both backend and frontend are running and `.env` files are set correctly.
- MongoDB must be running and accessible at the URL in your backend `.env`.

## License
This project is for educational/demo purposes.