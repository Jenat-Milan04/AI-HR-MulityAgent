# 🔒 SECURE API KEY SETUP

## Your Gemini API Key
**For your local setup, use this API key:**
```
your_gemini_api_key_here
```

## Setup Instructions
1. Copy `.env.example` to `.env`
2. Replace `your_gemini_api_key_here` with the key above
3. Keep your `.env` file local (never commit it)

## Example .env file
```
MODEL_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-flash
DB_PATH=./hr_agent.db
STM_MAX_ENTRIES=10
LTM_SIGNIFICANCE_THRESHOLD=0.7
REQUEST_TIMEOUT=10
MAX_RETRIES=3
```

**Note:** This file is gitignored and won't be pushed to GitHub for security.