from fastapi import FastAPI
import os
import uvicorn

# Environment Variables injected by Docker Compose
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

app = FastAPI(title="DTO Core Engine Base")

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "Digital Twin Factory - Core Engine Base",
        "connections": {
            "redis": REDIS_URL,
            "neo4j": NEO4J_URI
        },
        "message": "Start building your DTO logic here by modifying /app/main.py. Use n8n to connect workflows."
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
