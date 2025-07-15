# Dublin Rent Price Predictor

![](./dublin-rent-predictor-screenshot.png)

## Features
- Estimate the price of a property or shared room in Dublin.
- See model stats in the Model Info tab.
- Sign up and login to save your search history.

## Tech Stack
- Next.js 15
- Shadcn
- FastAPI
- Scikit-learn
- PostgreSQL
- Docker

---

## Getting Started

### Prerequisites
- Docker & Docker Compose
- AWS CLI configured with credentials

### Running Locally with Docker Compose

1.  **Create Backend Environment File:**
    Create a file at `src/backend/.env` with the following variables:
    ```env
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=postgres
    POSTGRES_DB=db
    POSTGRES_PORT=5432
    DATABASE_URL="postgresql+asyncpg://postgres:postgres@db:5432/db"
    SECRET_KEY="a-very-secret-key"
    ```

2.  **Create Frontend Environment File:**
    Create a file at `src/frontend/.env` with the following variable. This allows the frontend to communicate with the backend.
    ```env
    NEXT_PUBLIC_API_URL=http://localhost:8000
    ```

3.  **Run the Application:**
    Navigate to the `src` directory and run the following command:
    ```bash
    docker-compose up -d --build
    ```

4.  **Access the Application:**
    Open your browser and go to [http://localhost:3000](http://localhost:3000).
