"""Database setup and models for SQLite"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import json

DATABASE_PATH = "career_guidance.db"

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            firstName TEXT NOT NULL,
            lastName TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            gender TEXT NOT NULL,
            status TEXT NOT NULL,
            semester INTEGER NOT NULL,
            degreeProgram TEXT NOT NULL,
            degreeName TEXT NOT NULL,
            department TEXT NOT NULL,
            cgpa REAL NOT NULL,
            skills TEXT,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Questions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            correct_index INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Attempts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            category TEXT NOT NULL,
            answers TEXT NOT NULL,
            score INTEGER NOT NULL,
            max_score INTEGER NOT NULL,
            fit BOOLEAN NOT NULL,
            suggested_text TEXT NOT NULL,
            detailed TEXT,
            inducted BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

# Database helper functions
def create_user(user_data: Dict[str, Any]) -> int:
    """Create a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO users (username, firstName, lastName, email, gender, status, 
                          semester, degreeProgram, degreeName, department, cgpa, skills, password)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_data['username'], user_data['firstName'], user_data['lastName'],
        user_data['email'], user_data['gender'], user_data['status'],
        user_data['semester'], user_data['degreeProgram'], user_data['degreeName'],
        user_data['department'], user_data['cgpa'], user_data['skills'],
        user_data['password']
    ))
    
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return dict(row)
    return None

def get_questions_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all questions for a category"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    
    questions = []
    for row in rows:
        q = dict(row)
        q['options'] = json.loads(q['options'])
        questions.append(q)
    return questions

def insert_questions(questions: List[Dict[str, Any]]) -> int:
    """Insert multiple questions"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    count = 0
    for q in questions:
        cursor.execute("""
            INSERT INTO questions (category, question, options, correct_index)
            VALUES (?, ?, ?, ?)
        """, (
            q['category'],
            q['question'],
            json.dumps(q['options']),
            q['correct_index']
        ))
        count += 1
    
    conn.commit()
    conn.close()
    return count

def count_questions() -> int:
    """Count total questions in database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM questions")
    result = cursor.fetchone()
    conn.close()
    return result['count']

def create_attempt(attempt_data: Dict[str, Any]) -> int:
    """Create a new attempt"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO attempts (user_id, category, answers, score, max_score, 
                             fit, suggested_text, detailed)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        attempt_data['user_id'],
        attempt_data['category'],
        json.dumps(attempt_data['answers']),
        attempt_data['score'],
        attempt_data['max_score'],
        attempt_data['fit'],
        attempt_data['suggested_text'],
        json.dumps(attempt_data.get('detailed', []))
    ))
    
    attempt_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return attempt_id

def get_all_attempts() -> List[Dict[str, Any]]:
    """Get all attempts with user details"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.*, u.username, u.firstName, u.lastName, u.email, u.gender, 
               u.status, u.semester, u.degreeProgram, u.degreeName, 
               u.department, u.cgpa, u.skills
        FROM attempts a
        LEFT JOIN users u ON a.user_id = u.id
        ORDER BY a.created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    attempts = []
    for row in rows:
        attempt = dict(row)
        attempts.append(attempt)
    return attempts

def induct_student(attempt_id: int) -> bool:
    """Mark student as inducted"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE attempts 
        SET inducted = 1 
        WHERE id = ? AND fit = 1
    """, (attempt_id,))
    
    modified = cursor.rowcount
    conn.commit()
    conn.close()
    return modified > 0

def get_question_by_id(question_id: int) -> Optional[Dict[str, Any]]:
    """Get question by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        q = dict(row)
        q['options'] = json.loads(q['options'])
        return q
    return None
