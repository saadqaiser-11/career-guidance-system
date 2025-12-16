"""Career Guidance API with SQLite and Gemini"""
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import random
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import (
    init_db, create_user, get_user_by_email, get_user_by_id,
    get_questions_by_category, insert_questions, count_questions,
    create_attempt, get_all_attempts, induct_student, get_question_by_id
)
from gemini_service import GeminiService

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
ADMIN_USERNAME = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

app = FastAPI(title="Career Guidance API - SQLite + Gemini")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized")

# Initialize Gemini service
gemini_service = GeminiService()

# ---------- Models ----------
class SignUpModel(BaseModel):
    username: str
    firstName: str
    lastName: str
    email: EmailStr
    gender: str
    status: str
    semester: int
    degreeProgram: str
    degreeName: str
    department: str
    cgpa: float
    skills: Optional[str] = ""
    password: str

class SignInModel(BaseModel):
    email: EmailStr
    password: str

class AnswerItem(BaseModel):
    question_id: str
    selected_index: int

class SubmitRequest(BaseModel):
    user_id: str
    category: str
    answers: List[AnswerItem]

class SubmitResponse(BaseModel):
    user_id: str
    category: str
    score: int
    max_score: int
    fit: bool
    suggested_text: str
    timestamp: str

# ---------- Auth ----------
@app.post("/api/signup")
async def signup(data: SignUpModel):
    existing = get_user_by_email(data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_data = {
        "username": data.username,
        "firstName": data.firstName,
        "lastName": data.lastName,
        "email": data.email,
        "gender": data.gender,
        "status": data.status,
        "semester": data.semester,
        "degreeProgram": data.degreeProgram,
        "degreeName": data.degreeName,
        "department": data.department,
        "cgpa": data.cgpa,
        "skills": data.skills,
        "password": data.password  # hash in production
    }
    
    user_id = create_user(user_data)
    
    return {
        "user_id": str(user_id),
        "email": data.email,
        "name": f"{data.firstName} {data.lastName}"
    }

@app.post("/api/signin")
async def signin(data: SignInModel):
    # Check admin credentials
    if data.email == ADMIN_USERNAME and data.password == ADMIN_PASSWORD:
        return {
            "user_id": "admin",
            "email": data.email,
            "name": "Administrator",
        }
    
    # Check regular user
    user = get_user_by_email(data.email)
    if not user or user.get("password") != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {
        "user_id": str(user["id"]),
        "email": user["email"],
        "name": user.get("username", "")
    }

# ---------- Categories ----------
@app.get("/api/categories")
async def categories():
    cats = ["Backend", "Frontend", "Full Stack", "AI Engineer", "ML Engineer"]
    return {"categories": cats}

# ---------- Questions endpoint ----------
@app.get("/api/questions")
async def get_questions(category: str):
    """Generate fresh questions for the selected category using Gemini AI"""
    
    logger.info(f"Generating questions for category: {category}")
    
    # Generate 5 questions using Gemini
    prompt = (
        f"Generate exactly 5 multiple choice questions for {category} students. "
        "Each question must have: "
        "- a 'question' field (string), "
        "- an 'options' field (array of exactly 4 strings), "
        "- a 'correct_index' field (integer 0-3 indicating correct option). "
        "Return the output strictly as a JSON array of 5 objects. "
        "Make the questions practical and relevant to real-world {category} scenarios."
    )
    
    try:
        generated_questions = gemini_service.call_gemini(prompt, is_json=True)
        
        if not generated_questions:
            logger.error(f"Gemini failed to generate questions for {category}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to generate questions. Please check Gemini API configuration."
            )
        
        # Ensure it's a list
        if not isinstance(generated_questions, list):
            logger.error(f"Gemini response is not a list for {category}")
            raise HTTPException(status_code=500, detail="Invalid response format from AI")
        
        # Validate and store questions temporarily in database
        validated_questions = []
        for q in generated_questions:
            # Validate structure
            if not all(key in q for key in ['question', 'options', 'correct_index']):
                logger.warning(f"Skipping invalid question: {q}")
                continue
            
            if not isinstance(q['options'], list) or len(q['options']) != 4:
                logger.warning(f"Skipping question with invalid options: {q}")
                continue
            
            # Add category
            q['category'] = category
            validated_questions.append(q)
        
        if len(validated_questions) < 5:
            logger.warning(f"Only {len(validated_questions)} valid questions generated")
        
        # Store questions in database
        if validated_questions:
            insert_questions(validated_questions)
            logger.info(f"Stored {len(validated_questions)} questions for {category}")
        
        # Get the newly inserted questions
        all_category_questions = get_questions_by_category(category)
        
        # Return the latest 5 questions
        latest_questions = all_category_questions[-5:] if len(all_category_questions) >= 5 else all_category_questions
        
        out = []
        for q in latest_questions:
            out.append({
                "id": str(q["id"]),
                "category": q["category"],
                "question": q["question"],
                "options": q["options"]
            })
        
        logger.info(f"Successfully generated and returned {len(out)} questions for {category}")
        return {"questions": out}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questions for {category}: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error generating questions: {str(e)}"
        )

# ---------- Submit answers ----------
@app.post("/api/submit", response_model=SubmitResponse)
async def submit_answers(payload: SubmitRequest):
    # Verify user
    try:
        user_id = int(payload.user_id)
        user = get_user_by_id(user_id)
    except ValueError:
        user = None
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    total = 0
    max_score = len(payload.answers)
    detailed = []
    
    for ans in payload.answers:
        try:
            question_id = int(ans.question_id)
            q = get_question_by_id(question_id)
        except ValueError:
            q = None
        
        if not q:
            continue
        
        correct_index = q.get("correct_index", 0)
        is_correct = (ans.selected_index == correct_index)
        if is_correct:
            total += 1
        detailed.append({"q_id": ans.question_id, "is_correct": is_correct})
    
    score_percent = (total / max_score) * 100 if max_score > 0 else 0
    fit = score_percent >= 60
    
    if fit:
        suggested_text = (
            f"Based on your responses you score {total}/{max_score} ({int(score_percent)}%). "
            f"You show strong alignment with {payload.category}. Next: build small projects, practice domain-specific tasks, and follow tutorials."
        )
    else:
        suggested_text = (
            f"Your score is {total}/{max_score} ({int(score_percent)}%). "
            f"You may need more practice for {payload.category}. Suggested: strengthen fundamentals, try beginner projects, and re-test after practice."
        )
    
    attempt_data = {
        "user_id": user_id,
        "category": payload.category,
        "answers": [{"question_id": a.question_id, "selected_index": a.selected_index} for a in payload.answers],
        "score": total,
        "max_score": max_score,
        "fit": fit,
        "suggested_text": suggested_text,
        "detailed": detailed
    }
    
    create_attempt(attempt_data)
    timestamp = datetime.utcnow().isoformat()
    
    return SubmitResponse(
        user_id=payload.user_id,
        category=payload.category,
        score=total,
        max_score=max_score,
        fit=fit,
        suggested_text=suggested_text,
        timestamp=timestamp
    )

# ---------- Seed questions using Gemini (Optional - for pre-populating database) ----------
CATEGORIES = ["Backend", "Frontend", "Full Stack", "AI Engineer", "ML Engineer"]

@app.post("/api/seed_questions")
async def seed_questions():
    """
    Optional endpoint to pre-populate database with questions.
    Note: The /api/questions endpoint now generates questions dynamically,
    so this is only needed if you want to pre-seed the database.
    """
    
    all_questions = []
    
    for category in CATEGORIES:
        prompt = (
            f"Generate 20 multiple choice questions for {category} students. "
            "Each question must have: "
            "- a 'question' field (string), "
            "- an 'options' field (array of exactly 4 strings), "
            "- a 'correct_index' field (integer 0-3 indicating correct option). "
            "Return the output strictly as a JSON array of objects. "
            "Make questions practical and relevant to real-world scenarios."
        )
        
        logger.info(f"Pre-seeding questions for category: {category}")
        
        try:
            category_questions = gemini_service.call_gemini(prompt, is_json=True)
            
            if not category_questions:
                logger.error(f"Failed to generate questions for {category}")
                continue
            
            # Ensure it's a list
            if not isinstance(category_questions, list):
                logger.error(f"Response is not a list for {category}")
                continue
            
            # Add category field to each question
            for q in category_questions:
                q["category"] = category
            
            all_questions.extend(category_questions)
            logger.info(f"Generated {len(category_questions)} questions for {category}")
            
        except Exception as e:
            logger.error(f"Error generating questions for {category}: {e}")
            continue
    
    if not all_questions:
        raise HTTPException(status_code=500, detail="Failed to generate questions")
    
    # Insert into database
    inserted_count = insert_questions(all_questions)
    logger.info(f"Inserted {inserted_count} questions into database")
    
    return {
        "inserted": inserted_count, 
        "message": f"Successfully pre-seeded {inserted_count} questions",
        "note": "Questions are now generated dynamically per request"
    }

# ---------- Admin endpoints ----------
@app.get("/api/admin/results")
async def admin_results(
    username: str = Query(...),
    password: str = Query(...)
):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    attempts = get_all_attempts()
    
    results = []
    for doc in attempts:
        results.append({
            "id": doc["id"],
            "student_name": doc.get("username", ""),
            "firstName": doc.get("firstName", ""),
            "lastName": doc.get("lastName", ""),
            "email": doc.get("email", ""),
            "gender": doc.get("gender", ""),
            "status": doc.get("status", ""),
            "semester": doc.get("semester", 0),
            "degreeProgram": doc.get("degreeProgram", ""),
            "degreeName": doc.get("degreeName", ""),
            "department": doc.get("department", ""),
            "cgpa": doc.get("cgpa", 0.0),
            "skills": doc.get("skills", ""),
            "score": doc.get("score", 0),
            "max_score": doc.get("max_score", 0),
            "fit": bool(doc.get("fit", 0)),
            "inducted": bool(doc.get("inducted", 0)),
            "category": doc.get("category", "")
        })
    
    return results

@app.post("/api/admin/induct/{attempt_id}")
async def induct_student_endpoint(
    attempt_id: int,
    username: str = Query(...),
    password: str = Query(...)
):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    success = induct_student(attempt_id)
    
    if not success:
        raise HTTPException(status_code=400, detail="Cannot induct student")
    
    return {"message": "Student inducted"}

@app.get("/")
async def root():
    return {
        "message": "Career Guidance API",
        "database": "SQLite",
        "ai_service": "Google Gemini"
    }
