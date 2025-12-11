"""
Simplified Subtext API - Minimal MVP for deployment testing
Run with: uvicorn app_simple:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional, List
import os

# Simple in-memory storage for testing (replace with DB later)
USERS_DB = {}
MESSAGES_DB = []

app = FastAPI(
    title="Subtext API - Minimal MVP",
    description="Pocket Chief of Staff for office politics",
    version="0.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ============================================================================
# Schemas
# ============================================================================

class UserSignup(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MessageAnalyzeRequest(BaseModel):
    text: str
    sender_name: Optional[str] = None

class MessageAnalyzeResponse(BaseModel):
    subtext: str
    risk_level: str
    suggested_reply: str

# ============================================================================
# Simple Auth (no JWT for now, just tokens)
# ============================================================================

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Simple token validation"""
    token = credentials.credentials
    if token not in USERS_DB.values():
        raise HTTPException(status_code=401, detail="Invalid token")
    # Return email
    for email, user_token in USERS_DB.items():
        if user_token == token:
            return email
    raise HTTPException(status_code=401, detail="Invalid token")

# ============================================================================
# API Routes
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Subtext API - Minimal MVP",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "version": "0.1.0"}

@app.post("/auth/signup", response_model=TokenResponse)
async def signup(user_data: UserSignup):
    """Simple signup - stores in memory"""
    if user_data.email in USERS_DB:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Generate simple token (email + password hash)
    token = f"token_{user_data.email}_{hash(user_data.password)}"
    USERS_DB[user_data.email] = token

    return TokenResponse(access_token=token)

@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """Simple login"""
    if credentials.email not in USERS_DB:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Return existing token
    token = USERS_DB[credentials.email]
    return TokenResponse(access_token=token)

@app.post("/analyze", response_model=MessageAnalyzeResponse)
async def analyze_message(
    request: MessageAnalyzeRequest,
    current_user: str = Depends(get_current_user)
):
    """
    Analyze a message - FOR NOW: Returns mock data
    TODO: Integrate with Anthropic Claude API
    """

    # Mock analysis for testing deployment
    analysis = {
        "subtext": f"Analysis of message from {request.sender_name or 'unknown'}: This appears to be a strategic communication. The sender may be testing boundaries.",
        "risk_level": "medium",
        "suggested_reply": "Thank you for reaching out. Let me review this and get back to you with a thoughtful response."
    }

    # Store in memory
    MESSAGES_DB.append({
        "user": current_user,
        "text": request.text,
        "analysis": analysis
    })

    return MessageAnalyzeResponse(**analysis)

@app.get("/history")
async def get_history(current_user: str = Depends(get_current_user)):
    """Get analysis history"""
    user_messages = [
        msg for msg in MESSAGES_DB
        if msg.get("user") == current_user
    ]
    return {"messages": user_messages, "count": len(user_messages)}

@app.get("/stats")
async def get_stats():
    """Get system stats"""
    return {
        "total_users": len(USERS_DB),
        "total_analyses": len(MESSAGES_DB),
        "status": "running"
    }

# ============================================================================
# Run with: uvicorn app_simple:app --host 0.0.0.0 --port 8000
# ============================================================================
