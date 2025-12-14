# Full Stack Application

This repository contains a full stack application with a React frontend and a FastAPI backend.

## Tech Stack
- Frontend: React
- Backend: FastAPI (Python)
- Frontend Dev Server: Vite
- Backend Server: Uvicorn

## Frontend Setup (React)

### Prerequisites
- Node.js
- npm

### Install Dependencies
```bash
npm install
````

### Run Frontend

```bash
npm run dev
```

The frontend runs in development mode. The local URL will be shown in the terminal (typically [http://localhost:5173](http://localhost:5173)).

## Backend Setup (FastAPI)

### Prerequisites

* Python 3.9+
* pip
* (Optional) Virtual environment

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Backend

```bash
uvicorn main:app --reload
```

The backend will be available at:

* API: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* Swagger Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Running the Application

1. Start the backend using Uvicorn.
2. Start the frontend using npm.
3. Ensure the frontend API calls point to the correct backend URL.

## Notes

* Both frontend and backend must be running simultaneously.
* Update environment variables or configuration as required.
* This setup is intended for local development.

## License
This project is for development and learning purposes.