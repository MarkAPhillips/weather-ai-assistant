from typing import Dict, List, Optional
from datetime import datetime, timedelta
import uuid
from models import ChatSession, ChatMessage


class SessionManager:
    """Manages chat sessions and message history."""

    def __init__(self):
        self.sessions: Dict[str, ChatSession] = {}
        self.session_timeout = timedelta(hours=24) 

    def create_session(self) -> ChatSession:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        session = ChatSession(
            session_id=session_id,
            messages=[],
            created_at=now,
            last_activity=now
        )

        self.sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get a session by ID."""
        session = self.sessions.get(session_id)
        if session and self._is_session_valid(session):
            return session
        return None

    def add_message(self, session_id: str, role: str, content: str) -> Optional[ChatMessage]:
        """Add a message to a session."""
        session = self.get_session(session_id)
        if not session:
            return None

        message_id = str(uuid.uuid4())
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now().isoformat(),
            message_id=message_id
        )

        session.messages.append(message)
        session.last_activity = datetime.now().isoformat()

        return message

    def get_conversation_history(self, session_id: str, limit: int = 10) -> List[ChatMessage]:
        """Get recent conversation history."""
        session = self.get_session(session_id)
        if not session:
            return []

        # Return last N messages
        return session.messages[-limit:] if limit else session.messages

    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def list_sessions(self, limit: int = 50) -> List[ChatSession]:
        """List all active sessions."""
        valid_sessions = []
        for session in self.sessions.values():
            if self._is_session_valid(session):
                valid_sessions.append(session)

        # Sort by last activity (most recent first)
        valid_sessions.sort(key=lambda s: s.last_activity, reverse=True)
        return valid_sessions[:limit]

    def cleanup_expired_sessions(self) -> int:
        """Remove expired sessions."""
        expired_ids = []
        for session_id, session in self.sessions.items():
            if not self._is_session_valid(session):
                expired_ids.append(session_id)

        for session_id in expired_ids:
            del self.sessions[session_id]

        return len(expired_ids)

    def _is_session_valid(self, session: ChatSession) -> bool:
        """Check if a session is still valid (not expired)."""
        last_activity = datetime.fromisoformat(session.last_activity)
        return datetime.now() - last_activity < self.session_timeout

    def get_session_stats(self) -> Dict[str, int]:
        """Get session statistics."""
        total_sessions = len(self.sessions)
        active_sessions = len([s for s in self.sessions.values() if self._is_session_valid(s)])
        expired_sessions = total_sessions - active_sessions

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions
        }
