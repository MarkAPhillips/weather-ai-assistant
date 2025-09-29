import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ChatMessageComponent } from './chat-message.component';
import { ChatMessage } from '../models/chat.models';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('ChatMessageComponent', () => {
  let component: ChatMessageComponent;
  let fixture: ComponentFixture<ChatMessageComponent>;

  const mockUserMessage: ChatMessage = {
    role: 'user',
    content: 'Hello, how is the weather?',
    timestamp: '2024-01-15T10:30:00Z',
    message_id: 'msg-1'
  };

  const mockAssistantMessage: ChatMessage = {
    role: 'assistant',
    content: 'The weather is **sunny** and warm today!',
    timestamp: '2024-01-15T10:30:05Z',
    message_id: 'msg-2'
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatMessageComponent, NoopAnimationsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatMessageComponent);
    component = fixture.componentInstance;
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should render user message correctly', () => {
      component.message = mockUserMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const messageContent = compiled.querySelector('[data-testid="message-content"]');
      expect(messageContent).toBeTruthy();
      expect(messageContent.textContent).toContain('Hello, how is the weather?');
    });

    it('should render assistant message correctly', () => {
      component.message = mockAssistantMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const messageContent = compiled.querySelector('[data-testid="message-content"]');
      expect(messageContent).toBeTruthy();
      expect(messageContent.textContent).toContain('The weather is');
    });
  });

  describe('Avatar Display', () => {
    it('should show person icon for user messages', () => {
      component.message = mockUserMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('mat-icon')).toBeTruthy();
    });

    it('should show robot icon for assistant messages', () => {
      component.message = mockAssistantMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      expect(compiled.querySelector('mat-icon')).toBeTruthy();
    });
  });

  describe('Typewriter Effect', () => {
    it('should not show typewriter cursor (removed)', () => {
      component.message = mockAssistantMessage;
      component.typewriterActive = true;
      component.isLastMessage = true;
      fixture.detectChanges();

      // Check that typewriter cursor is no longer shown (removed)
      const compiled = fixture.nativeElement;
      const cursorElement = compiled.querySelector('[data-testid="typewriter-cursor"]');
      expect(cursorElement).toBeFalsy();
    });

    it('should emit skipTypewriter when clicked during typewriter', () => {
      spyOn(component.skipTypewriter, 'emit');
      component.message = mockAssistantMessage;
      component.typewriterActive = true;
      component.isLastMessage = true;
      fixture.detectChanges();

      const messageContent = fixture.nativeElement.querySelector('[data-testid="message-text"]');
      messageContent.click();

      expect(component.skipTypewriter.emit).toHaveBeenCalled();
    });
  });

  describe('Message Formatting', () => {
    it('should format bold text correctly', () => {
      component.message = mockAssistantMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const strongElement = compiled.querySelector('strong');
      expect(strongElement).toBeTruthy();
      expect(strongElement.textContent).toBe('☀️ sunny');
    });

    it('should add weather emojis to weather-related text', () => {
      const weatherMessage: ChatMessage = {
        role: 'assistant',
        content: 'It is sunny and warm today with light rain expected in the evening.',
        timestamp: '2024-01-15T10:30:05Z',
        message_id: 'msg-2'
      };
      
      component.message = weatherMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const messageText = compiled.querySelector('[data-testid="message-text"]');
      expect(messageText.innerHTML).toContain('☀️ sunny');
      expect(messageText.innerHTML).toContain('🌧️ rain');
    });

    it('should add temperature emojis', () => {
      const tempMessage: ChatMessage = {
        role: 'assistant',
        content: 'It will be hot during the day and cold at night.',
        timestamp: '2024-01-15T10:30:05Z',
        message_id: 'msg-3'
      };
      
      component.message = tempMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const messageText = compiled.querySelector('[data-testid="message-text"]');
      expect(messageText.innerHTML).toContain('🔥 hot');
      expect(messageText.innerHTML).toContain('🥶 cold');
    });

    it('should format timestamp correctly', () => {
      component.message = mockUserMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const timestampElement = compiled.querySelector('[data-testid="message-timestamp"]');
      // The timestamp format is "Mon, Jan 15th 10.30am" with . instead of :
      expect(timestampElement.textContent).toMatch(/\d{1,2}\.\d{2}/);
    });
  });

  describe('Layout Direction', () => {
    it('should reverse layout for user messages', () => {
      component.message = mockUserMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const messageContainer = compiled.querySelector('.flex');
      expect(messageContainer.classList.contains('flex-row-reverse')).toBeTruthy();
    });

    it('should not reverse layout for assistant messages', () => {
      component.message = mockAssistantMessage;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const messageContainer = compiled.querySelector('.flex');
      expect(messageContainer.classList.contains('flex-row-reverse')).toBeFalsy();
    });
  });
});
