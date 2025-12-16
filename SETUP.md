# Career Guidance System - Setup Guide

## Overview
Modern career guidance quiz system with:
- **Frontend**: React with green/white gradient theme
- **Backend**: FastAPI with SQLite database
- **AI**: Google Gemini for question generation

---

## Backend Setup

### 1. Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Gemini API (Optional - for question generation)
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# Get key from: https://makersuite.google.com/app/apikey
```

### 3. Start Backend Server
```bash
# Option 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python module
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend will run at: **http://localhost:8000**

---

## Frontend Setup

### 1. Install Node Dependencies
```bash
# From project root
npm install
```

### 2. Start Frontend Development Server
```bash
npm start
```

Frontend will run at: **http://localhost:3000**

---

## Initial Setup

### 1. Configure Gemini API Key (Required)
Questions are generated dynamically using Gemini AI, so you **must** configure your API key:

```bash
cd backend
# Edit .env file
GEMINI_API_KEY=your_actual_gemini_api_key_here
```

Get your API key from: https://makersuite.google.com/app/apikey

**Important**: Without a valid Gemini API key, the quiz won't work since questions are generated on-demand.

### 2. Admin Access
- **URL**: http://localhost:3000/admin
- **Username**: admin@gmail.com
- **Password**: admin123

---

## Database

The SQLite database (`career_guidance.db`) is created automatically in the `backend/` folder.

### Tables:
- **users**: Student profiles
- **questions**: Quiz questions
- **attempts**: Quiz results

---

## Features

### Student Flow:
1. Sign up with profile information
2. Sign in
3. Select a career category
4. Answer 5 random questions
5. Get score and career fit assessment

### Admin Flow:
1. Sign in with admin credentials
2. View all student results
3. Induct qualified students (score ≥ 60%)

### Categories:
- Backend
- Frontend
- Full Stack
- AI Engineer
- ML Engineer

---

## API Endpoints

### Public
- `POST /api/signup` - Register
- `POST /api/signin` - Login
- `GET /api/categories` - List categories
- `GET /api/questions?category={name}` - Get questions
- `POST /api/submit` - Submit answers

### Admin (requires auth)
- `GET /api/admin/results?username=admin@gmail.com&password=admin123`
- `POST /api/admin/induct/{id}?username=admin@gmail.com&password=admin123`

### Setup
- `POST /api/seed_questions` - Generate questions with Gemini

---

## Troubleshooting

### Backend won't start
- Check Python version (3.8+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is available

### Frontend won't start
- Check Node version (14+)
- Install dependencies: `npm install`
- Check port 3000 is available

### No questions available
- Run the seed endpoint: `POST /api/seed_questions`
- Check Gemini API key is valid
- Check backend logs for errors

### Database issues
- Delete `career_guidance.db` and restart backend
- Database will be recreated automatically

---

## Development

### Backend (FastAPI)
- Auto-reload enabled with `--reload` flag
- API docs: http://localhost:8000/docs
- Logs show in terminal

### Frontend (React)
- Hot reload enabled by default
- Changes reflect immediately
- Check browser console for errors

---

## Production Notes

- Hash passwords before storing (currently plain text)
- Use environment variables for secrets
- Configure CORS properly
- Use PostgreSQL instead of SQLite for scale
- Add rate limiting
- Implement proper authentication (JWT)
