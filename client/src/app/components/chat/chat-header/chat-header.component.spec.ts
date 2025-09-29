import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChatHeaderComponent } from './chat-header.component';
import { ChatSession } from '../models/chat.models';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('ChatHeaderComponent', () => {
  let component: ChatHeaderComponent;
  let fixture: ComponentFixture<ChatHeaderComponent>;

  const mockSession: ChatSession = {
    session_id: 'session-1',
    messages: [],
    created_at: '2024-01-15T10:30:00Z',
    last_activity: '2024-01-15T10:30:00Z'
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatHeaderComponent, NoopAnimationsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatHeaderComponent);
    component = fixture.componentInstance;
    component.showSessions = false; // Set default value
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should render header title', () => {
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('Chat');
    });

    it('should render toolbar', () => {
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('mat-toolbar')).toBeTruthy();
    });
  });

  describe('Event Emitters', () => {
    it('should emit newChatRequested when onNewChatRequested is called', () => {
      spyOn(component.newChatRequested, 'emit');

      component.onNewChatRequested();

      expect(component.newChatRequested.emit).toHaveBeenCalled();
    });

    it('should emit toggleSessions when onToggleSessions is called', () => {
      spyOn(component.toggleSessions, 'emit');

      component.onToggleSessions();

      expect(component.toggleSessions.emit).toHaveBeenCalled();
    });
  });

  describe('Component Properties', () => {
    it('should have default values', () => {
      expect(component.currentSession).toBeNull();
      expect(component.showSessions).toBeFalse();
    });

    it('should accept input properties', () => {
      component.currentSession = mockSession;
      component.showSessions = true;

      expect(component.currentSession).toEqual(mockSession);
      expect(component.showSessions).toBeTrue();
    });
  });

});
