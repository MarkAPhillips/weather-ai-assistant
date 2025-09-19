import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';


export interface ChatMessage {
  role: string;
  content: string;
  timestamp: string;
  message_id: string;
}

export interface ChatSession {
  session_id: string;
  messages: ChatMessage[];
  created_at: string;
  last_activity: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  message_id: string;
  timestamp: string;
}

export interface SessionStats {
  total_sessions: number;
  active_sessions: number;
  expired_sessions: number;
}

@Injectable({
  providedIn: 'root'
})
export class WeatherService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  // Chat endpoints
  sendChatMessage(request: ChatRequest): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat/send`, request);
  }

  getChatSessions(): Observable<{sessions: ChatSession[]}> {
    return this.http.get<{sessions: ChatSession[]}>(`${this.apiUrl}/chat/sessions`);
  }

  getChatSession(sessionId: string): Observable<ChatSession> {
    return this.http.get<ChatSession>(`${this.apiUrl}/chat/sessions/${sessionId}`);
  }

  deleteChatSession(sessionId: string): Observable<{message: string}> {
    return this.http.delete<{message: string}>(`${this.apiUrl}/chat/sessions/${sessionId}`);
  }

  createChatSession(): Observable<ChatSession> {
    return this.http.post<ChatSession>(`${this.apiUrl}/chat/sessions`, null);
  }

  getChatStats(): Observable<SessionStats> {
    return this.http.get<SessionStats>(`${this.apiUrl}/chat/stats`);
  }

  cleanupExpiredSessions(): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.apiUrl}/chat/cleanup`, {});
  }

  // Health check
  getHealth(): Observable<any> {
    return this.http.get(`${this.apiUrl}/health`);
  }
}
