# Career Guidance Backend

FastAPI backend with SQLite database and Google Gemini AI integration.

## Features

- **SQLite Database**: Lightweight, file-based database
- **Google Gemini AI**: Question generation using Gemini API
- **FastAPI**: Modern, fast web framework
- **RESTful API**: Clean API endpoints for frontend

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment variables**:
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your Gemini API key
GEMINI_API_KEY=your_actual_api_key_here
```

3. **Get Gemini API Key**:
   - Visit: https://makersuite.google.com/app/apikey
   - Create a new API key
   - Add it to your `.env` file

4. **Run the server**:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or with Python:
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Authentication
- `POST /api/signup` - Register new user
- `POST /api/signin` - User login

### Quiz
- `GET /api/categories` - Get available categories
- `GET /api/questions?category={category}` - Get questions for category
- `POST /api/submit` - Submit quiz answers

### Admin (requires credentials)
- `GET /api/admin/results` - Get all quiz results
- `POST /api/admin/induct/{attempt_id}` - Induct a student

### Setup
- `POST /api/seed_questions` - Generate questions using Gemini AI

## Admin Credentials

- **Username**: admin@gmail.com
- **Password**: admin123

## Database

The SQLite database (`career_guidance.db`) will be created automatically on first run.

### Tables:
- **users**: Student information
- **questions**: Quiz questions
- **attempts**: Quiz attempts and results

## Gemini Integration

### Dynamic Question Generation
The `/api/questions?category={category}` endpoint generates **fresh questions on-demand** using Google Gemini AI:
- Each request generates 5 new questions for the selected category
- Questions are stored in the database for record-keeping
- Ensures unique quiz experience every time

### Categories:
- Backend
- Frontend
- Full Stack
- AI Engineer
- ML Engineer

### Optional Pre-seeding
The `/api/seed_questions` endpoint can be used to pre-populate the database with questions, but it's not required since questions are generated dynamically.
