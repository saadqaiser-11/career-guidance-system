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

# Config
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "career_guidance_db")

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
    email: EmailStr
    password: str
    name: Optional[str] = None

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
        "email": data.email,
        "password": data.password,   # prototype only; hash in production
        "name": data.name or "",
        "created_at": datetime.utcnow()
    }
    res = await users_col.insert_one(user)
    user_id = str(res.inserted_id)
    return {"user_id": user_id, "email": data.email}

@app.post("/api/signin")
async def signin(data: SignInModel):
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

# ---------- Seed questions (dev only) ----------
@app.post("/api/seed_questions")
async def seed_questions():
    existing = await questions_col.count_documents({})
    if existing > 0:
        return {"inserted": 0, "message": "questions already exist"}
    samples = [
        # Backend
        {"category":"Backend", "question":"Which HTTP method is used to update resources?","options":["GET","POST","PUT","DELETE"], "correct_index":2},
        {"category":"Backend", "question":"What does REST stand for?","options":["Representational State Transfer","Remote Execution System","RESTful Endpoint","None"], "correct_index":0},
        {"category":"Backend", "question":"Which database is relational?","options":["MongoDB","MySQL","Cassandra","Redis"], "correct_index":1},
        {"category":"Backend", "question":"What is middleware in web frameworks?","options":["Client-side code","Database","Server-side layer between request and response","Styling tool"], "correct_index":2},
        {"category":"Backend", "question":"Which status code means success?","options":["200","404","500","302"], "correct_index":0},

        # Frontend
        {"category":"Frontend","question":"Which language is used for styling web pages?","options":["HTML","Python","CSS","SQL"], "correct_index":2},
        {"category":"Frontend","question":"Which JS method updates the DOM?","options":["fetch()","querySelector()","console.log()","setTimeout()"], "correct_index":1},
        {"category":"Frontend","question":"What is React primarily used for?","options":["Database","UI Library","Styling","Server"], "correct_index":1},
        {"category":"Frontend","question":"Which property controls flex container direction?","options":["align-items","flex-direction","display","position"], "correct_index":1},
        {"category":"Frontend","question":"Which tag defines a hyperlink in HTML?","options":["<link>","<a>","<href>","<nav>"], "correct_index":1},

        # Full Stack (mix)
        {"category":"Full Stack","question":"Which tool helps you version control code?","options":["VSCode","Git","Figma","Postman"], "correct_index":1},
        {"category":"Full Stack","question":"Which environment runs JavaScript on the server?","options":["Django","Flask","Node.js","Rails"], "correct_index":2},
        {"category":"Full Stack","question":"Which protocol is used by web browsers?","options":["FTP","HTTP","SMTP","SNMP"], "correct_index":1},
        {"category":"Full Stack","question":"What does CRUD stand for?","options":["Create Read Update Delete","Check Read Update Delete","Compute Read Update Deploy","Create Run Update Deploy"], "correct_index":0},
        {"category":"Full Stack","question":"Which database stores JSON-like documents?","options":["MySQL","MongoDB","OracleDB","Postgres"], "correct_index":1},

        # AI Engineer
        {"category":"AI Engineer","question":"Which library is commonly used for deep learning?","options":["pandas","numpy","tensorflow","flask"], "correct_index":2},
        {"category":"AI Engineer","question":"What is overfitting?","options":["Model underperforms on train data","Model performs well on unseen data","Model fits noise in training data","Model is perfectly generalized"], "correct_index":2},
        {"category":"AI Engineer","question":"Which activation function outputs between 0 and 1?","options":["ReLU","tanh","sigmoid","softmax"], "correct_index":2},
        {"category":"AI Engineer","question":"Which is a supervised learning task?","options":["Clustering","Classification","Dimensionality Reduction","None"], "correct_index":1},
        {"category":"AI Engineer","question":"What is gradient descent used for?","options":["Data preprocessing","Model optimization","Feature selection","Visualization"], "correct_index":1},

        # ML Engineer
        {"category":"ML Engineer","question":"What does bias-variance tradeoff refer to?","options":["Choosing wrong model","Balancing underfitting and overfitting","Feature engineering step","Hyperparameter tuning only"], "correct_index":1},
        {"category":"ML Engineer","question":"Which technique reduces dimensionality?","options":["PCA","Gradient Boosting","Cross Validation","Dropout"], "correct_index":0},
        {"category":"ML Engineer","question":"What is cross-validation used for?","options":["Testing speed","Model selection","Data cleaning","Deployment"], "correct_index":1},
        {"category":"ML Engineer","question":"Which model is good for tabular data?","options":["CNN","RNN","XGBoost","GAN"], "correct_index":2},
        {"category":"ML Engineer","question":"Which metric is used for regression problems?","options":["Accuracy","RMSE","Precision","F1-score"], "correct_index":1},
    ]
    res = await questions_col.insert_many(samples)
    return {"inserted": len(res.inserted_ids)}
