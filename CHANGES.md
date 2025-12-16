# Recent Changes - Dynamic Question Generation

## What Changed?

### Backend Behavior Update
The "Get Questions" button now **generates fresh questions dynamically** using Gemini AI instead of retrieving pre-seeded questions from the database.

## How It Works Now

### User Flow:
1. User selects a category (e.g., "Backend", "Frontend")
2. User clicks "Get Questions" button
3. **Backend calls Gemini API** to generate 5 fresh questions for that category
4. Questions are stored in database for record-keeping
5. Questions are returned to the user
6. User answers and submits

### Benefits:
✓ **Fresh questions every time** - No repetition
✓ **Dynamic content** - Questions adapt to current trends
✓ **Scalable** - No need to pre-populate database
✓ **Unique experience** - Each quiz attempt is different

## Technical Details

### Modified Endpoint: `GET /api/questions?category={category}`

**Before:**
- Retrieved random questions from database
- Required pre-seeding via `/api/seed_questions`

**After:**
- Generates 5 new questions using Gemini AI
- Stores them in database automatically
- Returns fresh questions immediately

### Code Changes:
- `backend/main.py` - Updated `/api/questions` endpoint
- Added Gemini API call with category-specific prompt
- Added validation for generated questions
- Auto-stores questions in database

### Requirements:
- **GEMINI_API_KEY** must be set in `backend/.env`
- Get key from: https://makersuite.google.com/app/apikey

## Optional: Pre-seeding

The `/api/seed_questions` endpoint still exists but is now **optional**:
- Can be used to pre-populate database with questions
- Not required for the quiz to work
- Useful for testing or offline scenarios

## Configuration

### backend/.env
```env
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

## Testing

1. Start backend: `cd backend && python -m uvicorn main:app --reload`
2. Start frontend: `npm start`
3. Sign up/Sign in
4. Select a category
5. Click "Get Questions"
6. Watch as Gemini generates fresh questions!

## Error Handling

If Gemini API fails:
- User sees error message: "Failed to generate questions"
- Check backend logs for details
- Verify API key is valid
- Check internet connection

## Database

Questions are still stored in SQLite for:
- Record keeping
- Analytics
- Audit trail
- Fallback if needed

## Performance

- Question generation takes 2-5 seconds
- Loading indicator shows during generation
- Questions cached in database after generation
- Subsequent requests for same category may use cached questions (if you modify the code to do so)

## Future Enhancements

Possible improvements:
- Cache questions per user session
- Add difficulty levels
- Generate more questions in background
- Add question rating system
- Implement question feedback loop
