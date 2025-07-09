# Dublin Rent Price Estimator

Web app to estimate Dublin rent prices.

![](./dublin-rent-predictor-screenshot.png)

## Features
- Estimate the price of a property or shared room in Dublin.
- See model stats in the Model Info tab.
- Sign up and login to save your search history.

## Tech Stack
- Next.js
- Shadcn UI
- FastAPI
- PostgreSQL
- Docker

# How to run the application

## 1. Run the backend

Run this command from the `src/backend` directory:

```bash
uv run uvicorn app.main:app --reload

or

python -m uvicorn app.main:app --reload
```

## 2. Run the frontend

Run this command from the `src/frontend` directory:

```bash
pnpm dev
```

## 3. Run the database

Run this command from the `src/backend` directory:

```bash
docker compose up -d
```

## PgAdmin

Connect to the database using PgAdmin to view the users and search history tables.

- Host name: localhost
- Port: 5432
- Database: postgres
- Maintainance database: postgres
- Username: postgres
- Password: postgres

## 4. View the application

Go to http://localhost:3000 to see the application.
