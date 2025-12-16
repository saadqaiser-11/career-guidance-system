# backend/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import os
import random
from datetime import datetime
from bson import ObjectId
from fastapi import Query 
# Config
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "career_guidance_db")
ADMIN_USERNAME = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"

app = FastAPI(title="Career Guidance API - Sprint 2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # set to frontend origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = AsyncIOMotorClient(MONGODB_URI)
db = client[DB_NAME]
users_col = db["users"]
questions_col = db["questions"]
attempts_col = db["attempts"]

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
    existing = await users_col.find_one({"email": data.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = {
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
        "password": data.password,  # hash in production
        "created_at": datetime.utcnow()
    }
    print("kuch bhi")
    res = await users_col.insert_one(user)
    print("kuch bhi")
    return {
        "user_id": str(res.inserted_id),
        "email": data.email,
        "name": f"{data.firstName} {data.lastName}"
    }


@app.post("/api/signin")
async def signin(data: SignInModel):
    if  data.email=="admin@gmail.com" and data.password== "admin123":
        return {
            "user_id": "admin",
            "email": data.email,
            "name": "Administrator",
        }
    
    user = await users_col.find_one({"email": data.email})
    if not user or user.get("password") != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"user_id": str(user["_id"]), "email": user["email"], "name": user.get("name","")}

# ---------- Categories ----------
@app.get("/api/categories")
async def categories():
    cats = ["Backend", "Frontend", "Full Stack", "AI Engineer", "ML Engineer"]
    return {"categories": cats}

# ---------- Questions endpoint ----------
@app.get("/api/questions")
async def get_questions(category: str):
    docs = await questions_col.find({"category": category}).to_list(length=100)
    print(len(docs))
    if not docs:
        raise HTTPException(status_code=404, detail="No questions for this category")
    sample = random.sample(docs, min(5, len(docs)))
    out = []
    for d in sample:
        out.append({
            "id": str(d["_id"]),
            "category": d["category"],
            "question": d["question"],
            "options": d["options"]
        })
    return {"questions": out}

# ---------- Submit answers ----------
@app.post("/api/submit", response_model=SubmitResponse)
async def submit_answers(payload: SubmitRequest):
    # verify user
    try:
        u = await users_col.find_one({"_id": ObjectId(payload.user_id)})
    except Exception:
        u = None
    if not u:
        raise HTTPException(status_code=404, detail="User not found")

    total = 0
    max_score = len(payload.answers)
    detailed = []
    for ans in payload.answers:
        try:
            q = await questions_col.find_one({"_id": ObjectId(ans.question_id)})
        except Exception:
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

    attempt_doc = {
        "user_id": ObjectId(payload.user_id),
        "category": payload.category,
        "answers": [a.dict() for a in payload.answers],
        "score": total,
        "max_score": max_score,
        "fit": fit,
        "suggested_text": suggested_text,
        "detailed": detailed,
        "created_at": datetime.utcnow()
    }
    res = await attempts_col.insert_one(attempt_doc)
    timestamp = attempt_doc["created_at"].isoformat()

    return SubmitResponse(
        user_id=payload.user_id,
        category=payload.category,
        score=total,
        max_score=max_score,
        fit=fit,
        suggested_text=suggested_text,
        timestamp=timestamp
    )

# ---------- Seed questions using Gemini/OpenAI ----------
import openai
import json
import os

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

CATEGORIES = ["Backend", "Frontend", "Full Stack", "AI Engineer", "ML Engineer"]

@app.post("/api/seed_questions")
async def seed_questions():
    # Check if DB already has questions
    existing = await questions_col.count_documents({})
    if existing > 0:
        return {"inserted": 0, "message": "questions already exist"}

    samples = []

    for category in CATEGORIES:
        prompt = (
            f"Generate 20 multiple choice questions for {category} students. "
            "Each question must have: "
            "- a 'question' field (string), "
            "- an 'options' field (list of 4 strings), "
            "- a 'correct_index' field (0-3 indicating correct option). "
            "Return the output strictly as a JSON array."
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )
            content = response.choices[0].message["content"]

            # Remove code block if present
            if content.startswith("```"):
                lines = content.split("\n")
                # Remove first and last line of ```json
                content = "\n".join(lines[1:-1])

            # Parse JSON safely
            category_questions = json.loads(content)

            # Add category field
            for q in category_questions:
                q["category"] = category
            samples.extend(category_questions)

        except Exception as e:
            print(f"Error generating questions for {category}: {e}")
            continue

    if not samples:
        raise HTTPException(status_code=500, detail="Failed to generate questions")

    # Insert into MongoDB
    res = await questions_col.insert_many(samples)
    return {"inserted": len(res.inserted_ids)}

@app.get("/api/admin/results")
async def admin_results(
    username: str = Query(...),
    password: str = Query(...)
):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    results = []
    async for doc in attempts_col.find():
        user = await users_col.find_one({"_id": doc["user_id"]})
        results.append({
            "id": str(doc["_id"]),
            "student_name": user.get("username", "") if user else- "",
            "firstName": user.get("firstName", "") if user else "",
            "lastName": user.get("lastName", "") if user else "",
            "email": user.get("email", "") if user else "",
            "gender": user.get("gender", "") if user else "",
            "status": user.get("status", "") if user else "",
            "semester": user.get("semester", 0) if user else 0,
            "degreeProgram": user.get("degreeProgram", "") if user else "",
            "degreeName": user.get("degreeName", "") if user else "",
            "department": user.get("department", "") if user else "",
            "cgpa": user.get("cgpa", 0.0) if user else 0.0,
            "skills": user.get("skills", "") if user else "",
            "score": doc.get("score", 0),
            "max_score": doc.get("max_score", 0),
            "fit": doc.get("fit", False),
            "inducted": doc.get("inducted", False),
            "category": doc.get("category", "")
        })

    return results
@app.post("/api/admin/induct/{attempt_id}")
async def induct_student(
    attempt_id: str,
    username: str = Query(...),
    password: str = Query(...)
):
    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Unauthorized")

    res = await attempts_col.update_one(
        {"_id": ObjectId(attempt_id), "fit": True},
        {"$set": {"inducted": True}}
    )

    if res.modified_count == 0:
        raise HTTPException(status_code=400, detail="Cannot induct student")

    return {"message": "Student inducted"}
