import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ChatComponent } from './chat.component';
import { WeatherService } from '../../services/weather.service';
import { ChatMessage, ChatSession, ChatResponse } from './models/chat.models';

describe('ChatComponent', () => {
  let component: ChatComponent;
  let fixture: ComponentFixture<ChatComponent>;
  let weatherService: jasmine.SpyObj<WeatherService>;
  let snackBar: jasmine.SpyObj<MatSnackBar>;

  const mockSessions: ChatSession[] = [
    {
      session_id: 'session-1',
      messages: [],
      created_at: '2024-01-15T10:30:00Z',
      last_activity: '2024-01-15T10:30:00Z'
    }
  ];

  const mockChatResponse: ChatResponse = {
    response: 'The weather is sunny today!',
    session_id: 'session-1',
    message_id: 'msg-1',
    timestamp: '2024-01-15T10:30:05Z'
  };

  beforeEach(async () => {
    const weatherServiceSpy = jasmine.createSpyObj('WeatherService', [
      'getHealth',
      'getChatSessions',
      'createChatSession',
      'getChatSession',
      'deleteChatSession',
      'sendChatMessage',
      'cleanupExpiredSessions'
    ]);

    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    await TestBed.configureTestingModule({
      imports: [
        ChatComponent,
        NoopAnimationsModule,
        HttpClientTestingModule
      ],
      providers: [
        { provide: WeatherService, useValue: weatherServiceSpy },
        { provide: MatSnackBar, useValue: snackBarSpy }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatComponent);
    component = fixture.componentInstance;
    weatherService = TestBed.inject(WeatherService) as jasmine.SpyObj<WeatherService>;
    snackBar = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;

    // Setup default mock responses
    weatherService.getHealth.and.returnValue(of({ 
      status: 'healthy',
      service: 'weather-ai',
      timestamp: '2024-01-15T10:30:00Z',
      components: {
        weather_agent: 'healthy',
        environment: 'healthy'
      }
    }));
    weatherService.getChatSessions.and.returnValue(of({ sessions: mockSessions }));
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should initialize with empty state', () => {
      expect(component.messages).toEqual([]);
      expect(component.displayedMessages).toEqual([]);
      expect(component.currentSession).toBeNull();
      expect(component.loading).toBeFalse();
    });

    it('should call health check and load sessions on init', () => {
      component.ngOnInit();

      expect(weatherService.getHealth).toHaveBeenCalled();
      expect(weatherService.getChatSessions).toHaveBeenCalled();
    });
  });

  describe('Session Management', () => {


    it('should load existing session', (done) => {
      const sessionToLoad: ChatSession = {
        session_id: 'session-1',
        messages: [
          {
            role: 'user',
            content: 'Hello',
            timestamp: '2024-01-15T10:30:00Z',
            message_id: 'msg-1'
          }
        ],
        created_at: '2024-01-15T10:30:00Z',
        last_activity: '2024-01-15T10:30:00Z'
      };

      weatherService.getChatSession.and.returnValue(of(sessionToLoad));

      component.loadSession(sessionToLoad);

      // Wait for async operations
      setTimeout(() => {
        expect(component.currentSession).toBe(sessionToLoad);
        expect(component.messages).toEqual(sessionToLoad.messages);
        expect(component.showSessionList).toBeFalse();
        done();
      }, 100);
    });

    it('should delete session successfully', () => {
      component.currentSession = mockSessions[0];
      weatherService.deleteChatSession.and.returnValue(of({ message: 'Deleted' }));

      component.deleteSession('session-1');

      expect(component.currentSession).toBeNull();
      expect(component.messages).toEqual([]);
      expect(component.displayedMessages).toEqual([]);
      expect(weatherService.getChatSessions).toHaveBeenCalled();
    });

    it('should cleanup sessions', () => {
      weatherService.cleanupExpiredSessions.and.returnValue(of({ message: 'Cleaned up 2 sessions' }));

      component.cleanupSessions();

      expect(weatherService.getChatSessions).toHaveBeenCalled();
    });
  });

  describe('Message Handling', () => {
    beforeEach(() => {
      component.currentSession = mockSessions[0];
    });

    it('should send message successfully', async () => {
      weatherService.sendChatMessage.and.returnValue(of(mockChatResponse));
      spyOn(component, 'updateDisplayedMessages').and.returnValue(Promise.resolve());
      spyOn(component, 'focusInput');

      await component.sendMessage('Hello');

      expect(component.messages.length).toBe(2);
      expect(component.messages[0].role).toBe('user');
      expect(component.messages[0].content).toBe('Hello');
      expect(component.messages[1].role).toBe('assistant');
      expect(component.messages[1].content).toBe('The weather is sunny today!');
      expect(component.loading).toBeFalse();
    });

    it('should not send empty message', () => {
      component.sendMessage('');
      component.sendMessage('   ');

      expect(weatherService.sendChatMessage).not.toHaveBeenCalled();
    });

    it('should not send message when loading', () => {
      component.loading = true;
      component.sendMessage('Hello');

      expect(weatherService.sendChatMessage).not.toHaveBeenCalled();
    });

  });

  describe('Typewriter Effect', () => {
    it('should apply typewriter effect to last AI message', async () => {
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: 'Hello world',
        timestamp: '2024-01-15T10:30:00Z',
        message_id: 'msg-1'
      };

      component.messages = [aiMessage];
      spyOn(component, 'typewriterEffect').and.returnValue(Promise.resolve());

      await component.updateDisplayedMessages();

      expect(component.typewriterEffect).toHaveBeenCalledWith(aiMessage, 0);
    });

    it('should skip typewriter effect', () => {
      component.typewriterActive = true;

      component.skipTypewriter();

      expect(component.typewriterActive).toBeFalse();
    });
  });

  describe('UI State Management', () => {
    it('should have session list visible by default', () => {
      expect(component.showSessionList).toBeTrue();
    });
  });


  describe('ViewChild References', () => {
    it('should have chatContainer ViewChild after view init', () => {
      fixture.detectChanges();
      expect(component.chatContainer).toBeDefined();
    });

    it('should have chatInput ViewChild after view init', () => {
      fixture.detectChanges();
      expect(component.chatInput).toBeDefined();
    });
  });

  describe('Lifecycle Hooks', () => {
    it('should call scrollToBottom in ngAfterViewChecked', () => {
      spyOn(component, 'scrollToBottom');

      component.ngAfterViewChecked();

      expect(component.scrollToBottom).toHaveBeenCalled();
    });
  });
});
