# 🔒 SECURE API KEY SETUP

## Your Gemini API Key
**For your local setup, use this API key:**
```
AQ.Ab8RN6ImQZ7btT_J_fVAiU16Y1To18_yRx_sOtP-SEbcUZv-2g
```

## Setup Instructions
1. Copy `.env.example` to `.env`
2. Replace `your_gemini_api_key_here` with the key above
3. Keep your `.env` file local (never commit it)

## Example .env file
```
MODEL_PROVIDER=gemini
GEMINI_API_KEY=AQ.Ab8RN6ImQZ7btT_J_fVAiU16Y1To18_yRx_sOtP-SEbcUZv-2g
MODEL_NAME=gemini-1.5-flash
DB_PATH=./hr_agent.db
STM_MAX_ENTRIES=10
LTM_SIGNIFICANCE_THRESHOLD=0.7
REQUEST_TIMEOUT=10
MAX_RETRIES=3
```

**Note:** This file is gitignored and won't be pushed to GitHub for security.