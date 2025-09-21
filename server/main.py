from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import os
import asyncio
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from weather_agent import WeatherAgent
from session_manager import SessionManager
from models import ChatRequest, ChatResponse
from dotenv import load_dotenv

load_dotenv()

# Initialize session manager
session_manager = SessionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("Starting Weather AI Assistant...")

    # Start background cleanup task
    cleanup_task = asyncio.create_task(periodic_cleanup())

    yield

    # Shutdown
    cleanup_task.cancel()
    print("Shutting down Weather AI Assistant...")


async def periodic_cleanup():
    """Periodically clean up expired sessions."""
    while True:
        try:
            await asyncio.sleep(3600)  # Run every hour
            cleaned_count = session_manager.cleanup_expired_sessions()
            if cleaned_count > 0:
                print(f"Cleaned up {cleaned_count} expired sessions")
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f"Cleanup error: {e}")

app = FastAPI(
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None,
    openapi_url="/openapi.json" if os.getenv("ENVIRONMENT") != "production" else None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

weather_agent = WeatherAgent(
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    weather_api_key=os.getenv("OPENWEATHER_API_KEY"),
)


# Chat endpoints
@app.post("/api/chat/send", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest):
    """Send a message and get AI response."""
    try:
        # Get or create session
        if request.session_id:
            session = session_manager.get_session(request.session_id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
        else:
            session = session_manager.create_session()

        # Add user message to session
        user_message = session_manager.add_message(
            session.session_id, "user", request.message
        )

        if not user_message:
            raise HTTPException(status_code=500, detail="Failed to add message")

        # Get conversation history
        conversation_history = session_manager.get_conversation_history(session.session_id)

        # Get AI response with context
        ai_response = weather_agent.get_weather_advice(
            query=request.message,
            conversation_history=conversation_history
        )

        # Add AI response to session
        ai_message = session_manager.add_message(
            session.session_id, "assistant", ai_response
        )

        return ChatResponse(
            response=ai_response,
            session_id=session.session_id,
            message_id=ai_message.message_id,
            timestamp=ai_message.timestamp
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/sessions")
async def list_sessions():
    """List all active chat sessions."""
    try:
        sessions = session_manager.list_sessions()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/sessions/{session_id}")
async def get_session(session_id: str):
    """Get a specific chat session."""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chat/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session."""
    try:
        success = session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/sessions")
async def create_session():
    """Create a new chat session."""
    try:
        session = session_manager.create_session()
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/chat/sessions")
async def delete_all_sessions():
    """Delete all chat sessions."""
    try:
        deleted_count = session_manager.delete_all_sessions()
        return {"message": f"Deleted {deleted_count} sessions"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/chat/stats")
async def get_chat_stats():
    """Get chat session statistics."""
    try:
        stats = session_manager.get_session_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat/cleanup")
async def cleanup_expired_sessions():
    """Clean up expired sessions."""
    try:
        cleaned_count = session_manager.cleanup_expired_sessions()
        return {"message": f"Cleaned up {cleaned_count} expired sessions"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint with service status."""
    try:
        # Check if weather agent is properly initialized
        agent_status = "healthy" if weather_agent else "unhealthy"

        # Check environment variables
        google_key = os.getenv("GOOGLE_API_KEY")
        weather_key = os.getenv("OPENWEATHER_API_KEY")
        env_status = "healthy" if google_key and weather_key else "unhealthy"

        overall_status = (
            "healthy" if agent_status == "healthy" and env_status == "healthy"
            else "unhealthy"
        )

        return {
            "status": overall_status,
            "service": "weather-ai",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "components": {
                "weather_agent": agent_status,
                "environment": env_status
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "weather-ai",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
