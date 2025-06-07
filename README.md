# dublin-rent-price-estimator
Web app to estimate Dublin rent prices

## Done 
- Daft scraper
- Set up the new Next.js frontend
- Build out the initial frontend UI using Shadcn with dummy data
- Implement a simple backend with dummy data using FastAPI
- Add the sharing dataset too so that users can select 'single room' and 'double room' as well as 'studio' or the number of bedrooms

## To do
- Add error bars to the prediction
- Show the percentile of the price compared to other samples in the dataset with the same number of bedrooms and bathrooms
- Containerize the application and deploy it to AWS in several different ways

# How to run the application


## Backend

Run this command from the `src/backend` directory:

```bash
uvicorn app.main:app --reload
```

## Frontend

Run this command from the `src/frontend` directory:

```bash
pnpm dev
```

## Database

Run this command from the `src/backend` directory:

```bash
docker compose up -d
```