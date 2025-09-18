import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { WeatherService, ChatMessage, ChatSession, ChatRequest } from '../../services/weather.service';

@Component({
  selector: 'app-chat',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './chat.component.html',
})
export class ChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('chatContainer') chatContainer!: ElementRef;
  @ViewChild('messageInput') messageInput!: ElementRef;

  // Chat state
  messages: ChatMessage[] = [];
  displayedMessages: ChatMessage[] = [];
  currentSession: ChatSession | null = null;
  userMessage: string = '';
  loading: boolean = false;
  error: string = '';
  typewriterActive: boolean = false;


  // Session management
  sessions: ChatSession[] = [];
  showSessionList: boolean = false;

  constructor(private weatherService: WeatherService) { }

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
  }

  loadSession(sessionId: string): void {
    this.weatherService.getChatSession(sessionId).subscribe({
      next: async (session) => {
        this.currentSession = session;
        this.messages = session.messages;
        this.displayedMessages = [...session.messages]; // Load all messages without typewriter effect
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
        this.loadSessions();
        if (this.currentSession?.session_id === sessionId) {
          this.currentSession = null;
          this.messages = [];
          this.displayedMessages = [];
        }
      },
      error: (err) => {
        this.error = 'Failed to delete session: ' + err.message;
      }
    });
  }

  async sendMessage(): Promise<void> {
    if (!this.userMessage.trim() || this.loading) return;

    const request: ChatRequest = {
      message: this.userMessage.trim(),
      session_id: this.currentSession?.session_id
    };

    this.loading = true;
    this.error = '';

    this.weatherService.sendChatMessage(request).subscribe({
      next: async (response) => {
        // Update current session
        this.currentSession = {
          session_id: response.session_id,
          messages: [...this.messages, {
            role: 'user',
            content: this.userMessage.trim(),
            timestamp: new Date().toISOString(),
            message_id: 'temp-user-' + Date.now()
          }, {
            role: 'assistant',
            content: response.response,
            timestamp: response.timestamp,
            message_id: response.message_id
          }],
          created_at: this.currentSession?.created_at || new Date().toISOString(),
          last_activity: response.timestamp
        };

        this.messages = this.currentSession.messages;
        this.userMessage = '';
        this.loadSessions();
        this.focusInput();
        
        // Apply typewriter effect to the new AI response
        await this.updateDisplayedMessages();
      },
      error: (err) => {
        this.error = 'Failed to send message: ' + err.message;
        this.loading = false;
      },
      complete: () => {
        this.loading = false;
      }
    });
  }

  onKeyPress(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  focusInput(): void {
    setTimeout(() => {
      this.messageInput.nativeElement.focus();
    }, 100);
  }

  formatTimestamp(timestamp: string): string {
    return new Date(timestamp).toLocaleTimeString();
  }

  formatMessageContent(content: string): string {
    // Convert **text** to <strong>text</strong>
    return content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  }

  getSessionPreview(session: ChatSession): string {
    const lastMessage = session.messages[session.messages.length - 1];
    if (!lastMessage) return 'Empty session';
    
    // Remove markdown formatting for preview
    const cleanContent = lastMessage.content.replace(/\*\*(.*?)\*\*/g, '$1');
    return cleanContent.substring(0, 50) + (cleanContent.length > 50 ? '...' : '');
  }

  cleanupSessions(): void {
    this.weatherService.cleanupExpiredSessions().subscribe({
      next: (response) => {
        console.log(response.message);
        this.loadSessions();
      },
      error: (err) => {
        this.error = 'Failed to cleanup sessions: ' + err.message;
      }
    });
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
      
      // Add a small delay between characters with slight variation for realism
      const delay = 15 + Math.random() * 10; // 15-25ms delay
      await new Promise(resolve => setTimeout(resolve, delay));
    }
    
    // Ensure the final message is complete
    this.displayedMessages[index] = {
      ...typewriterMessage,
      content: fullText
    };
    
    this.typewriterActive = false;
  }

  async updateDisplayedMessages(): Promise<void> {
    // Stop any active typewriter effect
    this.typewriterActive = false;
    
    // Wait a bit to ensure the effect stops
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Update displayed messages to match actual messages
    this.displayedMessages = [...this.messages];
    
    // Apply typewriter effect to the last assistant message if it's new
    if (this.messages.length > 0) {
      const lastMessage = this.messages[this.messages.length - 1];
      if (lastMessage.role === 'assistant') {
        const lastIndex = this.messages.length - 1;
        await this.typewriterEffect(lastMessage, lastIndex);
      }
    }
  }

  skipTypewriter(): void {
    // Stop typewriter effect and show full message immediately
    this.typewriterActive = false;
    this.displayedMessages = [...this.messages];
  }
}
