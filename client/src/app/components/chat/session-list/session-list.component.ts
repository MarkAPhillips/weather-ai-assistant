import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ChatSession } from '../models/chat.models';

@Component({
  selector: 'app-session-list',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatSnackBarModule,
    MatTooltipModule
  ],
  templateUrl: './session-list.component.html'
})
export class SessionListComponent {
  @Input() sessions: ChatSession[] = [];
  @Input() currentSession: ChatSession | null = null;
  @Output() sessionSelected = new EventEmitter<ChatSession>();
  @Output() sessionDeleted = new EventEmitter<string>();
  @Output() cleanupRequested = new EventEmitter<void>();
  @Output() clearAllRequested = new EventEmitter<void>();

  private snackBar = inject(MatSnackBar);

  formatDate(date: string): string {
    return new Date(date).toLocaleDateString();
  }

  getFirstUserMessage(session: ChatSession): string {
    if (!session.messages || session.messages.length === 0) {
      return 'Empty session';
    }
    
    // Find the first user message
    const firstUserMessage = session.messages.find(msg => msg.role === 'user');
    
    if (!firstUserMessage) {
      return 'No user messages';
    }
    
    // Truncate long messages and clean up formatting
    let content = firstUserMessage.content.trim();
    
    // Remove markdown formatting for cleaner display
    content = content.replace(/\*\*(.*?)\*\*/g, '$1'); // Remove bold formatting
    content = content.replace(/\*(.*?)\*/g, '$1'); // Remove italic formatting
    
    // Truncate if too long
    if (content.length > 50) {
      content = content.substring(0, 47) + '...';
    }
    
    return content || 'Empty message';
  }

  getSessionsWithMessages(): ChatSession[] {
    if (!this.sessions || this.sessions.length === 0) {
      return [];
    }
    
    // Filter out sessions that have no user messages
    return this.sessions.filter(session => {
      return session.messages && session.messages.some(msg => msg.role === 'user');
    });
  }

  hasOldSessions(): boolean {
    if (!this.sessions || this.sessions.length === 0) {
      return false;
    }
    
    const now = new Date();
    const twentyFourHoursAgo = new Date(now.getTime() - (24 * 60 * 60 * 1000));
    
    return this.sessions.some(session => {
      const sessionDate = new Date(session.created_at);
      return sessionDate < twentyFourHoursAgo;
    });
  }

  onSessionSelected(session: ChatSession): void {
    this.sessionSelected.emit(session);
  }

  onSessionDeleted(sessionId: string): void {
    this.sessionDeleted.emit(sessionId);
  }

  onCleanupRequested(): void {
    this.cleanupRequested.emit();
    this.showCleanupToast();
  }

  onClearAllRequested(): void {
    this.clearAllRequested.emit();
    this.showClearAllToast();
  }

  showCleanupToast(): void {
    this.snackBar.open('Removing old chat sessions...', 'Close', {
      duration: 2000,
      horizontalPosition: 'center',
      verticalPosition: 'top',
      panelClass: ['cleanup-toast']
    });
  }

  private showClearAllToast(): void {
    this.snackBar.open('Deleting all chat sessions...', 'Close', {
      duration: 2000,
      horizontalPosition: 'center',
      verticalPosition: 'top',
      panelClass: ['cleanup-toast']
    });
  }
}