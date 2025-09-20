import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChatHeaderComponent } from './chat-header.component';
import { ChatSession } from '../models/chat.models';

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
      imports: [ChatHeaderComponent]
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

    it('should render New Chat button', () => {
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('New Chat');
    });

    it('should render Sessions button', () => {
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('Sessions');
    });
  });

  describe('New Chat Button', () => {
    it('should emit newChatRequested when clicked', () => {
      spyOn(component.newChatRequested, 'emit');
      fixture.detectChanges();

      const newChatButton = fixture.nativeElement.querySelector('button:first-child');
      newChatButton.click();

      expect(component.newChatRequested.emit).toHaveBeenCalled();
    });

    it('should have correct styling', () => {
      fixture.detectChanges();

      const newChatButton = fixture.nativeElement.querySelector('button:first-child');
      expect(newChatButton.classList.contains('bg-blue-600')).toBeTruthy();
      expect(newChatButton.classList.contains('hover:bg-blue-700')).toBeTruthy();
    });
  });

  describe('Sessions Button', () => {
    it('should emit toggleSessions when clicked', () => {
      spyOn(component.toggleSessions, 'emit');
      fixture.detectChanges();

      const sessionsButton = fixture.nativeElement.querySelector('button:last-child');
      sessionsButton.click();

      expect(component.toggleSessions.emit).toHaveBeenCalled();
    });

    it('should have correct styling', () => {
      fixture.detectChanges();

      const sessionsButton = fixture.nativeElement.querySelector('button:last-child');
      expect(sessionsButton.classList.contains('bg-gray-600')).toBeTruthy();
      expect(sessionsButton.classList.contains('hover:bg-gray-700')).toBeTruthy();
    });
  });

  describe('Button Layout', () => {
    it('should have buttons in correct order', () => {
      fixture.detectChanges();

      const buttons = fixture.nativeElement.querySelectorAll('button');
      expect(buttons[0].textContent.trim()).toBe('New Chat');
      expect(buttons[1].textContent.trim()).toBe('Sessions');
    });

    it('should have proper spacing between buttons', () => {
      fixture.detectChanges();

      const buttonContainer = fixture.nativeElement.querySelector('.flex.items-center.space-x-2');
      expect(buttonContainer).toBeTruthy();
    });
  });

  describe('Header Layout', () => {
    it('should have proper flex layout', () => {
      fixture.detectChanges();

      const header = fixture.nativeElement.querySelector('.flex.items-center.justify-between');
      expect(header).toBeTruthy();
    });

    it('should have border bottom', () => {
      fixture.detectChanges();

      const header = fixture.nativeElement.querySelector('.border-b.border-gray-200');
      expect(header).toBeTruthy();
    });
  });

  describe('Input Properties', () => {
    it('should accept currentSession input', () => {
      component.currentSession = mockSession;
      fixture.detectChanges();

      expect(component.currentSession).toBe(mockSession);
    });

    it('should handle null currentSession', () => {
      component.currentSession = null;
      fixture.detectChanges();

      expect(component.currentSession).toBeNull();
    });

    it('should accept showSessions input', () => {
      component.showSessions = true;
      fixture.detectChanges();

      expect(component.showSessions).toBe(true);
    });
  });

  describe('Toggle Sessions Button', () => {
    it('should show "Sessions" label on toggle', () => {
      component.showSessions = false;
      fixture.detectChanges();
      
      const toggle = fixture.debugElement.nativeElement.querySelector('mat-slide-toggle');
      const label = toggle.querySelector('.mat-slide-toggle-label');
      expect(label.textContent.trim()).toBe('Sessions');
    });

    it('should emit toggleSessions event when clicked', () => {
      spyOn(component.toggleSessions, 'emit');
      
      const toggle = fixture.debugElement.nativeElement.querySelector('mat-slide-toggle');
      toggle.click();
      
      expect(component.toggleSessions.emit).toHaveBeenCalled();
    });

    it('should have correct checked state when sessions are visible', () => {
      component.showSessions = true;
      fixture.detectChanges();
      
      const toggle = fixture.debugElement.nativeElement.querySelector('mat-slide-toggle');
      expect(toggle.classList.contains('mat-checked')).toBe(true);
    });

    it('should have correct unchecked state when sessions are hidden', () => {
      component.showSessions = false;
      fixture.detectChanges();
      
      const toggle = fixture.debugElement.nativeElement.querySelector('mat-slide-toggle');
      expect(toggle.classList.contains('mat-checked')).toBe(false);
    });
  });
});
