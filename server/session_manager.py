from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
import uuid
from models import ChatSession, ChatMessage


class SessionManager:
    """Manages chat sessions and message history."""

    def __init__(self):
        # Structure: {user_id: {session_id: ChatSession}}
        self.user_sessions: Dict[str, Dict[str, ChatSession]] = {}
        self.session_timeout = timedelta(hours=24)

    def create_session(self, user_id: str) -> ChatSession:
        """Create a new chat session for a specific user."""
        session_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        session = ChatSession(
            session_id=session_id,
            messages=[],
            created_at=now,
            last_activity=now
        )

        # Initialize user sessions if not exists
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {}

        self.user_sessions[user_id][session_id] = session
        return session

    def get_session(self, session_id: str,
                    user_id: str) -> Optional[ChatSession]:
        """Get a session by ID for a specific user."""
        if user_id not in self.user_sessions:
            return None

        session = self.user_sessions[user_id].get(session_id)
        if session and self._is_session_valid(session):
            return session
        return None

    def add_message(self, session_id: str, role: str, content: str,
                    user_id: str) -> Optional[ChatMessage]:
        """Add a message to a session."""
        session = self.get_session(session_id, user_id)
        if not session:
            return None

        message_id = str(uuid.uuid4())
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(timezone.utc).isoformat(),
            message_id=message_id
        )

        session.messages.append(message)
        session.last_activity = datetime.now(timezone.utc).isoformat()

        return message

    def get_conversation_history(self, session_id: str, user_id: str,
                                 limit: int = 10) -> List[ChatMessage]:
        """Get recent conversation history."""
        session = self.get_session(session_id, user_id)
        if not session:
            return []

        # Return last N messages
        return session.messages[-limit:] if limit else session.messages

    def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session for a specific user."""
        if (user_id in self.user_sessions and
                session_id in self.user_sessions[user_id]):
            del self.user_sessions[user_id][session_id]
            return True
        return False

    def delete_all_sessions(self, user_id: str) -> int:
        """Delete all sessions for a specific user."""
        if user_id not in self.user_sessions:
            return 0

        count = len(self.user_sessions[user_id])
        self.user_sessions[user_id].clear()
        return count

    def list_sessions(self, user_id: str,
                      limit: int = 50) -> List[ChatSession]:
        """List all active sessions for a specific user."""
        if user_id not in self.user_sessions:
            return []

        valid_sessions = []
        for session in self.user_sessions[user_id].values():
            if self._is_session_valid(session):
                valid_sessions.append(session)

        # Sort by last activity (most recent first)
        valid_sessions.sort(key=lambda s: s.last_activity, reverse=True)
        return valid_sessions[:limit]

    def cleanup_expired_sessions(self, user_id: str) -> int:
        """Remove expired sessions for a specific user."""
        if user_id not in self.user_sessions:
            return 0

        expired_ids = []
        for session_id, session in self.user_sessions[user_id].items():
            if not self._is_session_valid(session):
                expired_ids.append(session_id)

        for session_id in expired_ids:
            del self.user_sessions[user_id][session_id]

        return len(expired_ids)

    def _is_session_valid(self, session: ChatSession) -> bool:
        """Check if a session is still valid (not expired)."""
        last_activity = datetime.fromisoformat(session.last_activity)
        return (datetime.now(timezone.utc) - last_activity <
                self.session_timeout)

    def get_session_stats(self, user_id: str) -> Dict[str, int]:
        """Get session statistics for a specific user."""
        if user_id not in self.user_sessions:
            return {
                "total_sessions": 0,
                "active_sessions": 0,
                "expired_sessions": 0
            }

        total_sessions = len(self.user_sessions[user_id])
        active_sessions = len([
            s for s in self.user_sessions[user_id].values()
            if self._is_session_valid(s)])
        expired_sessions = total_sessions - active_sessions

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "expired_sessions": expired_sessions
        }
