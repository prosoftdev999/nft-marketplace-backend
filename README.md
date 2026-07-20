# NFT Marketplace Backend

A production-ready NFT Marketplace Backend built with FastAPI, PostgreSQL, Redis, and MinIO.

## Features

- JWT Authentication
- User Registration & Login
- NFT CRUD
- Collection CRUD
- NFT Listings
- NFT Favorites
- Search NFTs
- Image Upload with MinIO
- PostgreSQL Database
- Redis Cache
- Alembic Migrations
- Docker Support
- Pytest Test Suite
- GitHub Actions CI

---

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Redis
- MinIO
- Docker
- Pytest

---

## Project Structure

```
app/
├── api/
├── core/
├── db/
├── models/
├── repositories/
├── routes/
├── schemas/
├── services/

tests/

alembic/
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/prosoftdev999/nft-marketplace-backend.git
cd nft-marketplace-backend
```

Create environment file

```bash
cp .env.example .env
```

Run Docker

```bash
docker compose up --build -d
```

API Documentation

```
http://localhost:8001/docs
```

Health Check

```
http://localhost:8001/health
```

---

## Running Tests

```bash
pytest -v
```

or

```bash
docker compose exec api pytest -v
```

---

## Docker Services

- FastAPI
- PostgreSQL
- Redis
- MinIO

---

## API Endpoints

### Authentication

- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET /api/v1/auth/me

### Collections

- CRUD Collections

### NFTs

- CRUD NFTs

### Listings

- Create Listing
- Buy Listing
- Delete Listing

### Favorites

- Add Favorite
- Remove Favorite
- List Favorites

### Uploads

- Upload NFT Images

### Search

- Search NFTs

---

## Test Status

```
10 tests passed
```

---

## License

MIT License