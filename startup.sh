#!/bin/bash
# Quick local startup script
set -e

echo "=== CivicPulse Local Setup ==="

# Backend
echo "[1/4] Installing Python dependencies..."
pip install -r requirements.txt

# Frontend
echo "[2/4] Installing frontend dependencies..."
cd frontend && npm install && cd ..

# Env check
if [ ! -f ".env" ]; then
  echo "[3/4] Creating .env from example (fill in GEMINI_API_KEY)..."
  cp .env.example .env
else
  echo "[3/4] .env already exists"
fi

if [ ! -f "frontend/.env" ]; then
  echo "[4/4] Creating frontend/.env from example (fill in VITE_MAPS_API_KEY)..."
  cp frontend/.env.example frontend/.env
else
  echo "[4/4] frontend/.env already exists"
fi

echo ""
echo "=== Ready! ==="
echo "Backend:  cd backend && uvicorn main:app --reload"
echo "Frontend: cd frontend && npm run dev"
echo "API Docs: http://localhost:8000/docs"
