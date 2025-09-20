import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatSnackBar, MatSnackBarModule } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatSlideToggleModule } from '@angular/material/slide-toggle';
import { WeatherService } from '../../services/weather.service';
import { ChatMessage, ChatSession } from './models/chat.models';
import { ChatMessageComponent } from './chat-message/chat-message.component';
import { ChatInputComponent } from './chat-input/chat-input.component';
import { SessionListComponent } from './session-list/session-list.component';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [
    CommonModule,
    MatSnackBarModule,
    MatIconModule,
    MatButtonModule,
    MatSlideToggleModule,
    ChatMessageComponent,
    ChatInputComponent,
    SessionListComponent
  ],
  templateUrl: './chat.component.html',
  styles: [`
    ::ng-deep .mat-mdc-slide-toggle .mdc-form-field {
      color: white !important;
    }
    
    ::ng-deep .mat-mdc-slide-toggle.mdc-switch--checked .mdc-switch__track {
      background-color: #10b981 !important;
    }
    
    ::ng-deep .mat-mdc-slide-toggle:not(.mdc-switch--checked) .mdc-switch__track {
      background-color: #ef4444 !important;
    }
  `]
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('chatContainer') chatContainer!: ElementRef;
  @ViewChild('chatInput') chatInput!: ChatInputComponent;

  // Chat state
  messages: ChatMessage[] = [];
  displayedMessages: ChatMessage[] = [];
  currentSession: ChatSession | null = null;
  loading: boolean = false;
  error: string = '';
  typewriterActive: boolean = false;

  // Session management
  sessions: ChatSession[] = [];
  showSessionList: boolean = true; // Changed to true to show by default

  constructor(private weatherService: WeatherService, private cdr: ChangeDetectorRef, private snackBar: MatSnackBar) { }

  ngOnInit(): void {
    this.checkHealth();
    this.loadSessions();
    this.displayedMessages = [...this.messages];
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  scrollToBottom(): void {
    try {
      this.chatContainer.nativeElement.scrollTop = this.chatContainer.nativeElement.scrollHeight;
    } catch(err) { }
  }

  checkHealth(): void {
    this.weatherService.getHealth().subscribe({
      next: (data) => console.log('Backend health:', data),
      error: (err) => console.error('Backend health check failed:', err)
    });
  }

  loadSessions(): void {
    this.weatherService.getChatSessions().subscribe({
      next: (data) => {
        this.sessions = data.sessions;
        this.error = ''; // Clear any previous errors
      },
      error: (err) => {
        console.error('Failed to load sessions:', err);
        this.error = 'Failed to load sessions: ' + err.message;
      }
    });
  }

  createNewSession(): void {
    // If there's already a current session, create a new one
    if (this.currentSession) {
      this.weatherService.createChatSession().subscribe({
        next: (session) => {
          this.currentSession = session;
          this.messages = [];
          this.displayedMessages = [];
          this.loadSessions();
          this.focusInput();
        },
        error: (err) => {
          this.error = 'Failed to create session: ' + err.message;
        }
      });
    } else {
      // If no current session, just clear the messages without creating a new session
      this.messages = [];
      this.displayedMessages = [];
      this.focusInput();
    }
  }

  loadSession(session: ChatSession): void {
    this.weatherService.getChatSession(session.session_id).subscribe({
      next: (sessionData) => {
        this.currentSession = sessionData;
        this.messages = sessionData.messages;
        this.displayedMessages = [...this.messages];
        this.showSessionList = false;
        this.focusInput();
      },
      error: (err) => {
        this.error = 'Failed to load session: ' + err.message;
      }
    });
  }

  deleteSession(sessionId: string): void {
    this.weatherService.deleteChatSession(sessionId).subscribe({
      next: () => {
        if (this.currentSession?.session_id === sessionId) {
          this.currentSession = null;
          this.messages = [];
          this.displayedMessages = [];
        }
        this.loadSessions();
      },
      error: (err) => {
        this.error = 'Failed to delete session: ' + err.message;
      }
    });
  }

  sendMessage(message: string): void {
    if (!message.trim() || this.loading) return;

    this.loading = true;
    this.error = '';

    const request = {
      message: message.trim(),
      session_id: this.currentSession?.session_id
    };

    this.weatherService.sendChatMessage(request).subscribe({
      next: async (response) => {
        // Add user message
        const userMessage: ChatMessage = {
          role: 'user',
          content: message.trim(),
          timestamp: new Date().toISOString(),
          message_id: 'temp-user-' + Date.now()
        };
        this.messages.push(userMessage);

        // Add AI response
        const aiMessage: ChatMessage = {
          role: 'assistant',
          content: response.response,
          timestamp: response.timestamp,
          message_id: response.message_id
        };
        this.messages.push(aiMessage);

        // Check if this was a new session before updating currentSession
        const wasNewSession = !this.currentSession;

        // Update current session
        this.currentSession = {
          session_id: response.session_id,
          messages: this.messages,
          created_at: this.currentSession?.created_at || new Date().toISOString(),
          last_activity: response.timestamp
        };

        // Always refresh the sessions list to update message counts
        this.loadSessions();

        // Stop loading immediately when response arrives
        this.loading = false;
        this.cdr.detectChanges(); // Force change detection to hide loading indicator

        // Then start typewriter effect
        await this.updateDisplayedMessages();
        this.focusInput();
      },
      error: (err) => {
        this.error = 'Failed to send message: ' + err.message;
        this.loading = false;
        this.cdr.detectChanges(); // Force change detection
      }
    });
  }

  async updateDisplayedMessages(): Promise<void> {
    this.displayedMessages = [...this.messages];
    
    // Apply typewriter effect to the last AI message
    const lastMessage = this.messages[this.messages.length - 1];
    if (lastMessage && lastMessage.role === 'assistant') {
      const lastIndex = this.messages.length - 1;
      await this.typewriterEffect(lastMessage, lastIndex);
    }
  }

  async typewriterEffect(message: ChatMessage, index: number): Promise<void> {
    this.typewriterActive = true;
    const fullText = message.content;
    let currentText = '';
    
    // Create a copy of the message with empty content for typewriter effect
    const typewriterMessage: ChatMessage = {
      ...message,
      content: ''
    };
    
    // Add the message to displayed messages
    this.displayedMessages[index] = typewriterMessage;
    
    // Type out each character
    for (let i = 0; i < fullText.length; i++) {
      if (!this.typewriterActive) break; // Stop if component is destroyed or new message starts
      
      currentText += fullText[i];
      this.displayedMessages[index] = {
        ...typewriterMessage,
        content: currentText
      };
      
      // Random delay between 15-25ms for natural typing effect
      const delay = Math.random() * 10 + 15;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    this.typewriterActive = false;
  }

  skipTypewriter(): void {
    this.typewriterActive = false;
    // The last message will be fully displayed on the next change detection cycle
  }

  toggleSessionList(): void {
    this.showSessionList = !this.showSessionList;
    this.cdr.detectChanges(); // Force change detection
  }

  cleanupSessions(): void {
    this.weatherService.cleanupExpiredSessions().subscribe({
      next: (response) => {
        this.loadSessions();
        this.snackBar.open('Sessions cleaned up successfully!', 'Close', {
          duration: 3000,
          horizontalPosition: 'center',
          verticalPosition: 'top',
          panelClass: ['success-toast']
        });
      },
      error: (err) => {
        this.error = 'Failed to cleanup sessions: ' + err.message;
        this.snackBar.open('Failed to cleanup sessions', 'Close', {
          duration: 3000,
          horizontalPosition: 'center',
          verticalPosition: 'top',
          panelClass: ['error-toast']
        });
      }
    });
  }

  clearAllSessions(): void {
    this.weatherService.deleteAllSessions().subscribe({
      next: (response) => {
        this.currentSession = null;
        this.messages = [];
        this.displayedMessages = [];
        this.loadSessions();
        this.snackBar.open('All sessions deleted successfully!', 'Close', {
          duration: 3000,
          horizontalPosition: 'center',
          verticalPosition: 'top',
          panelClass: ['success-toast']
        });
      },
      error: (err) => {
        this.error = 'Failed to delete all sessions: ' + err.message;
        this.snackBar.open('Failed to delete all sessions', 'Close', {
          duration: 3000,
          horizontalPosition: 'center',
          verticalPosition: 'top',
          panelClass: ['error-toast']
        });
      }
    });
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
    
    // Truncate if too long (longer limit for header)
    if (content.length > 80) {
      content = content.substring(0, 77) + '...';
    }
    
    return content || 'Empty message';
  }

  focusInput(): void {
    setTimeout(() => {
      this.chatInput.focus();
    }, 100);
  }
}
