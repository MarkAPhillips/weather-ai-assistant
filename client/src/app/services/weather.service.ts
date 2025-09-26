import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { ChatMessage, ChatSession, ChatRequest, ChatResponse, SessionStats, HealthResponse } from '../components/chat/models/chat.models';



@Injectable({
  providedIn: 'root'
})
export class WeatherService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) { }

  // Chat endpoints
  sendChatMessage(request: ChatRequest, userId: string): Observable<ChatResponse> {
    return this.http.post<ChatResponse>(`${this.apiUrl}/chat/send?user_id=${userId}`, request);
  }

  getChatSessions(userId: string): Observable<{sessions: ChatSession[]}> {
    return this.http.get<{sessions: ChatSession[]}>(`${this.apiUrl}/chat/sessions?user_id=${userId}`);
  }

  getChatSession(sessionId: string, userId: string): Observable<ChatSession> {
    return this.http.get<ChatSession>(`${this.apiUrl}/chat/sessions/${sessionId}?user_id=${userId}`);
  }

  deleteChatSession(sessionId: string, userId: string): Observable<{message: string}> {
    return this.http.delete<{message: string}>(`${this.apiUrl}/chat/sessions/${sessionId}?user_id=${userId}`);
  }

  createChatSession(userId: string): Observable<ChatSession> {
    return this.http.post<ChatSession>(`${this.apiUrl}/chat/sessions?user_id=${userId}`, null);
  }

  getChatStats(): Observable<SessionStats> {
    return this.http.get<SessionStats>(`${this.apiUrl}/chat/stats`);
  }

  cleanupExpiredSessions(userId: string): Observable<{message: string}> {
    return this.http.post<{message: string}>(`${this.apiUrl}/chat/cleanup?user_id=${userId}`, {});
  }

  deleteAllSessions(userId: string): Observable<{message: string}> {
    return this.http.delete<{message: string}>(`${this.apiUrl}/chat/sessions?user_id=${userId}`);
  }

  // Health check
  getHealth(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(`${this.apiUrl}/health`);
  }
}
