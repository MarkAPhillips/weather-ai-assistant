import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { MatToolbarModule } from '@angular/material/toolbar';
import { ChatSession } from '../models/chat.models';

@Component({
  selector: 'app-chat-header',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatSlideToggleModule, MatToolbarModule],
  template: `
    <mat-toolbar class="bg-white/5 backdrop-blur-sm border-b border-white/10 px-4">
      <span class="text-lg font-medium text-white">Chat</span>
      <span class="flex-1"></span>
    </mat-toolbar>
  `
})
export class ChatHeaderComponent {
  @Input() currentSession: ChatSession | null = null;
  @Input() showSessions: boolean = false;
  @Output() newChatRequested = new EventEmitter<void>();
  @Output() toggleSessions = new EventEmitter<void>();

  onNewChatRequested(): void {
    this.newChatRequested.emit();
  }

  onToggleSessions(): void {
    this.toggleSessions.emit();
  }
}
