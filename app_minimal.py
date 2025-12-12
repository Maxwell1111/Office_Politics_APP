"""
ABSOLUTE BARE MINIMUM API - Just to prove deployment works
One health check endpoint only
"""

from fastapi import FastAPI
import os

app = FastAPI(title="Subtext Test")

@app.on_event("startup")
async def startup_event():
    port = os.environ.get("PORT", "unknown")
    print(f"🚀 App starting up! PORT={port}")
    print(f"✅ FastAPI app initialized")

@app.get("/")
def root():
    return {"message": "API is running", "status": "ok", "port": os.environ.get("PORT", "not set")}

@app.get("/health")
def health():
    return {"status": "ok"}

# That's it. More logging for debugging.
