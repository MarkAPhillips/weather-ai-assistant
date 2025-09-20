import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatSnackBar } from '@angular/material/snack-bar';
import { SessionListComponent } from './session-list.component';
import { ChatSession } from '../models/chat.models';

describe('SessionListComponent', () => {
  let component: SessionListComponent;
  let fixture: ComponentFixture<SessionListComponent>;
  let mockSnackBar: jasmine.SpyObj<MatSnackBar>;

  const mockSessions: ChatSession[] = [
    {
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
    },
    {
      session_id: 'session-2',
      messages: [
        {
          role: 'user',
          content: 'Hi there',
          timestamp: '2024-01-15T11:00:00Z',
          message_id: 'msg-2'
        },
        {
          role: 'assistant',
          content: 'Hello! How can I help?',
          timestamp: '2024-01-15T11:00:05Z',
          message_id: 'msg-3'
        }
      ],
      created_at: '2024-01-15T11:00:00Z',
      last_activity: '2024-01-15T11:00:05Z'
    }
  ];

  beforeEach(async () => {
    mockSnackBar = jasmine.createSpyObj('MatSnackBar', ['open']);
    
    await TestBed.configureTestingModule({
      imports: [SessionListComponent],
      providers: [
        { provide: MatSnackBar, useValue: mockSnackBar }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(SessionListComponent);
    component = fixture.componentInstance;
    component.sessions = mockSessions;
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should render sessions list', () => {
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const sessionElements = compiled.querySelectorAll('.space-y-2 > div');
      expect(sessionElements.length).toBe(2);
    });

    it('should show empty state when no sessions', () => {
      component.sessions = [];
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('No sessions created');
    });
  });

  describe('Session Display', () => {
    it('should display session ID correctly', () => {
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('session-1');
      expect(compiled.textContent).toContain('session-2');
    });

    it('should display message count correctly', () => {
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('1 messages');
      expect(compiled.textContent).toContain('2 messages');
    });

    it('should format dates correctly', () => {
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const dateElements = compiled.querySelectorAll('.text-xs.text-gray-500');
      expect(dateElements.length).toBeGreaterThan(0);
    });
  });

  describe('Current Session Highlighting', () => {
    it('should highlight current session', () => {
      component.currentSession = mockSessions[0];
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const highlightedSession = compiled.querySelector('.bg-blue-50');
      expect(highlightedSession).toBeTruthy();
    });

    it('should not highlight when no current session', () => {
      component.currentSession = null;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const highlightedSession = compiled.querySelector('.bg-blue-50');
      expect(highlightedSession).toBeFalsy();
    });
  });

  describe('Session Selection', () => {
    it('should emit sessionSelected when session is clicked', () => {
      spyOn(component.sessionSelected, 'emit');
      fixture.detectChanges();

      const sessionElement = fixture.nativeElement.querySelector('.cursor-pointer');
      sessionElement.click();

      expect(component.sessionSelected.emit).toHaveBeenCalledWith(mockSessions[0]);
    });
  });

  describe('Session Deletion', () => {
    it('should emit sessionDeleted when delete button is clicked', () => {
      spyOn(component.sessionDeleted, 'emit');
      fixture.detectChanges();

      const deleteButton = fixture.nativeElement.querySelector('button[title="Delete session"]');
      deleteButton.click();

      expect(component.sessionDeleted.emit).toHaveBeenCalledWith('session-1');
    });

    it('should stop propagation when delete button is clicked', () => {
      spyOn(component.sessionSelected, 'emit');
      spyOn(component.sessionDeleted, 'emit');
      fixture.detectChanges();

      const sessionElement = fixture.nativeElement.querySelector('.cursor-pointer');
      const deleteButton = fixture.nativeElement.querySelector('button[title="Delete session"]');
      
      deleteButton.click();

      expect(component.sessionDeleted.emit).toHaveBeenCalled();
      expect(component.sessionSelected.emit).not.toHaveBeenCalled();
    });
  });

  describe('Cleanup Functionality', () => {
    it('should emit cleanupRequested when cleanup button is clicked', () => {
      spyOn(component.cleanupRequested, 'emit');
      fixture.detectChanges();

      const cleanupButton = fixture.nativeElement.querySelector('button:not([title])');
      cleanupButton.click();

      expect(component.cleanupRequested.emit).toHaveBeenCalled();
    });
  });

  describe('Session Stats', () => {
    it('should display session count when sessions exist', () => {
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('Total: 2 sessions');
    });

    it('should not display stats when no sessions', () => {
      component.sessions = [];
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.textContent).not.toContain('Total:');
    });
  });

  describe('Date Formatting', () => {
    it('should handle invalid timestamps gracefully', () => {
      const invalidSession: ChatSession = {
        session_id: 'invalid-session',
        messages: [],
        created_at: 'invalid-date',
        last_activity: 'invalid-date'
      };

      component.sessions = [invalidSession];
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.textContent).toContain('invalid-date');
    });
  });

  describe('Cleanup Functionality', () => {
    it('should emit cleanupRequested event when cleanup button is clicked', () => {
      spyOn(component.cleanupRequested, 'emit');
      
      const cleanupButton = fixture.debugElement.nativeElement.querySelector('.cleanup-button');
      cleanupButton.click();
      
      expect(component.cleanupRequested.emit).toHaveBeenCalled();
    });

    it('should show cleanup toast when cleanup is requested', () => {
      component.onCleanupRequested();
      
      expect(mockSnackBar.open).toHaveBeenCalledWith(
        'Cleaning up expired sessions...',
        'Close',
        jasmine.objectContaining({
          duration: 3000,
          horizontalPosition: 'center',
          verticalPosition: 'top',
          panelClass: ['cleanup-toast']
        })
      );
    });
  });
});
