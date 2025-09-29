import { ComponentFixture, TestBed } from '@angular/core/testing';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { ChatInputComponent } from './chat-input.component';
import { FormsModule } from '@angular/forms';

describe('ChatInputComponent', () => {
  let component: ChatInputComponent;
  let fixture: ComponentFixture<ChatInputComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChatInputComponent, FormsModule, NoopAnimationsModule]
    }).compileComponents();

    fixture = TestBed.createComponent(ChatInputComponent);
    component = fixture.componentInstance;
  });

  describe('Component Initialization', () => {
    it('should create', () => {
      expect(component).toBeTruthy();
    });

    it('should initialize with empty message', () => {
      expect(component.message).toBe('');
    });
  });

  describe('Message Input', () => {
    it('should update message when typing', () => {
      fixture.detectChanges();
      component.message = 'Hello world';
      fixture.detectChanges();

      expect(component.message).toBe('Hello world');
    });

    it('should disable input when loading', async () => {
      fixture.detectChanges(); // Initial detection
      await fixture.whenStable(); // Wait for async operations
      
      component.loading = true;
      fixture.detectChanges(); // Detect loading change
      await fixture.whenStable(); // Wait for rendering

      const input = fixture.nativeElement.querySelector('[data-testid="message-input"]');
      expect(input).toBeTruthy();
      expect(input.disabled).toBeTruthy();
    });

    it('should enable input when not loading', () => {
      component.loading = false;
      fixture.detectChanges();

      const input = fixture.nativeElement.querySelector('[data-testid="message-input"]');
      expect(input.disabled).toBeFalsy();
    });
  });

  describe('Send Button', () => {
    it('should be disabled when message is empty', () => {
      component.message = '';
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('[data-testid="send-button"]');
      expect(button.disabled).toBeTruthy();
    });

    it('should be disabled when message is only whitespace', () => {
      component.message = '   ';
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('[data-testid="send-button"]');
      expect(button.disabled).toBeTruthy();
    });

    it('should be enabled when message has content', () => {
      component.message = 'Hello world';
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('[data-testid="send-button"]');
      expect(button.disabled).toBeFalsy();
    });

    it('should be disabled when loading', () => {
      component.message = 'Hello world';
      component.loading = true;
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('[data-testid="send-button"]');
      expect(button.disabled).toBeTruthy();
    });
  });

  describe('Send Message', () => {
    it('should emit sendMessage when clicking send button', () => {
      spyOn(component.sendMessage, 'emit');
      component.message = 'Hello world';
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('[data-testid="send-button"]');
      button.click();

      expect(component.sendMessage.emit).toHaveBeenCalledWith('Hello world');
    });

    it('should emit sendMessage when pressing Enter', () => {
      spyOn(component.sendMessage, 'emit');
      component.message = 'Hello world';
      fixture.detectChanges();

      const input = fixture.nativeElement.querySelector('[data-testid="message-input"]');
      input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter' }));

      expect(component.sendMessage.emit).toHaveBeenCalledWith('Hello world');
    });

    it('should clear message after sending', () => {
      component.message = 'Hello world';
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('[data-testid="send-button"]');
      button.click();

      expect(component.message).toBe('');
    });

    it('should not emit when message is empty', () => {
      spyOn(component.sendMessage, 'emit');
      component.message = '';
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('[data-testid="send-button"]');
      button.click();

      expect(component.sendMessage.emit).not.toHaveBeenCalled();
    });

    it('should not emit when loading', () => {
      spyOn(component.sendMessage, 'emit');
      component.message = 'Hello world';
      component.loading = true;
      fixture.detectChanges();

      const button = fixture.nativeElement.querySelector('[data-testid="send-button"]');
      button.click();

      expect(component.sendMessage.emit).not.toHaveBeenCalled();
    });
  });

  describe('Focus Management', () => {
    it('should focus input when focus method is called', () => {
      fixture.detectChanges();
      const input = fixture.nativeElement.querySelector('[data-testid="message-input"]');
      spyOn(input, 'focus');

      component.focus();

      expect(input.focus).toHaveBeenCalled();
    });

    it('should clear message when clear method is called', () => {
      component.message = 'Hello world';
      component.clear();

      expect(component.message).toBe('');
    });
  });
});
