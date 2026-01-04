from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import config
from config.settings import ALLOWED_ORIGINS, ENVIRONMENT

# Import routers
from routes import chat, history, feedback, analytics, health

app = FastAPI(
    title="AI Guru Multibot API",
    description="Secure AI Chat API with MongoDB integration",
    version="2.0.0",
    docs_url="/docs" if ENVIRONMENT != 'production' else None,
    redoc_url=None
)

# Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    return response

# Secure CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# Register Routers
app.include_router(health.router)
app.include_router(chat.router)
app.include_router(history.router)
app.include_router(feedback.router)
app.include_router(analytics.router)

if __name__ == "__main__":
    print("🚀 Starting AI Guru Multibot Backend...")
    print(f"📡 API Documentation: http://localhost:8001/docs" if ENVIRONMENT != 'production' else "📡 API Running in production mode")
    uvicorn.run(app, host="0.0.0.0", port=8001)