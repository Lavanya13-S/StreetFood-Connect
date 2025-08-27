# StreetConnect Frontend

This is the frontend (React) application for the StreetConnect platform, which connects street food vendors with trusted suppliers. The app provides vendor and supplier dashboards, product browsing, order management, analytics, and more.

## Features
- Vendor and supplier registration/login
- Product browsing and search
- Order placement and management
- Analytics dashboard for vendors and suppliers
- PDF invoice generation
- Responsive, modern UI

## Prerequisites
- Node.js (v16 or higher recommended)
- npm (comes with Node.js)
- The backend server running (see backend README for setup)

## Getting Started

1. **Install dependencies:**
   ```sh
   npm install
   ```

2. **Configure API URL:**
   - The frontend expects the backend API URL to be set in an environment variable. Create a `.env` file in this directory with:
     ```sh
     REACT_APP_BACKEND_URL=http://localhost:8000
     ```
   - Adjust the URL if your backend runs elsewhere.

3. **Start the frontend:**
   ```sh
   npm start
   ```
   The app will run at [http://localhost:3000](http://localhost:3000).

4. **Backend:**
   - Make sure the backend server is running on the correct port (default: 8000).

## Project Structure
- `src/` — Main React source code
- `public/` — Static files
- `App.js` — Main application logic

## Notes
- This project was bootstrapped with Create React App, but most default documentation has been removed for clarity.
- For development, both frontend and backend must be running.
- For production builds, use `npm run build`.

## Troubleshooting
- If you see network errors (e.g., 401 or 400), check that the backend is running and accessible at the URL set in `.env`.
- For form autofill and accessibility, all form fields have `name`, `id`, `autocomplete`, and `label` attributes.

## License
This project is for educational/demo purposes.
