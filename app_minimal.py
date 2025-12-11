"""
ABSOLUTE BARE MINIMUM API - Just to prove deployment works
One health check endpoint only
"""

from fastapi import FastAPI

app = FastAPI(title="Subtext Test")

@app.get("/")
def root():
    return {"message": "API is running", "status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}

# That's it. 15 lines total.
