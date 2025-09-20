import { Component, Input, Output, EventEmitter, ViewChild, ElementRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';

@Component({
  selector: 'app-chat-input',
  standalone: true,
  imports: [CommonModule, FormsModule, MatButtonModule, MatInputModule, MatFormFieldModule],
  template: `
    <div class="p-4 border-t border-white/10 bg-white/5 backdrop-blur-sm">
      <div class="flex space-x-2">
        <mat-form-field appearance="fill" class="flex-1">
          <mat-label class="text-slate-300">Type your message...</mat-label>
          <input
            #messageInput
            matInput
            [(ngModel)]="message"
            (keydown.enter)="onSendMessage()"
            [disabled]="loading"
            class="text-white placeholder-slate-400"
          />
        </mat-form-field>
        <button
          mat-raised-button
          color="primary"
          (click)="onSendMessage()"
          [disabled]="loading || !message.trim()"
          class="text-sm px-4 py-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span *ngIf="!loading">Send</span>
          <span *ngIf="loading" class="flex items-center">
            <div class="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            Sending...
          </span>
        </button>
      </div>
      
      <!-- Error Display -->
      <div *ngIf="error" class="mt-2 text-red-300 text-sm">
        {{ error }}
      </div>
    </div>
  `,
  styles: [`
    ::ng-deep .mat-mdc-form-field {
      --mdc-filled-text-field-container-color: rgba(255, 255, 255, 0.05);
      --mdc-filled-text-field-active-indicator-color: rgba(147, 51, 234, 0.8);
      --mdc-filled-text-field-hover-state-layer-color: rgba(255, 255, 255, 0.1);
    }
    
    ::ng-deep .mat-mdc-form-field .mat-mdc-text-field-wrapper {
      background-color: rgba(255, 255, 255, 0.05) !important;
      border: none !important;
      border-radius: 8px !important;
    }
    
    ::ng-deep .mat-mdc-form-field .mat-mdc-text-field-wrapper .mat-mdc-form-field-flex {
      border: none !important;
    }
    
    ::ng-deep .mat-mdc-form-field .mat-mdc-text-field-wrapper .mat-mdc-form-field-flex .mat-mdc-floating-label {
      color: rgba(203, 213, 225, 0.8) !important;
    }
    
    ::ng-deep .mat-mdc-form-field .mat-mdc-text-field-wrapper .mat-mdc-form-field-flex .mat-mdc-floating-label.mdc-floating-label--float-above {
      color: rgba(203, 213, 225, 0.6) !important;
    }
    
    ::ng-deep .mat-mdc-form-field input {
      color: white !important;
      border: none !important;
      outline: none !important;
      background: transparent !important;
    }
    
    ::ng-deep .mat-mdc-form-field input::placeholder {
      color: rgba(148, 163, 184, 0.6) !important;
    }
    
    ::ng-deep .mat-mdc-form-field .mat-mdc-text-field-wrapper .mat-mdc-form-field-flex .mat-mdc-form-field-infix {
      border: none !important;
    }
    
    ::ng-deep .mat-mdc-form-field .mat-mdc-text-field-wrapper .mat-mdc-form-field-flex .mat-mdc-form-field-infix::before {
      border: none !important;
    }
    
    ::ng-deep .mat-mdc-form-field .mat-mdc-text-field-wrapper .mat-mdc-form-field-flex .mat-mdc-form-field-infix::after {
      border: none !important;
    }
    
    ::ng-deep .mat-mdc-form-field .mat-mdc-text-field-wrapper .mat-mdc-form-field-flex .mat-mdc-form-field-infix .mat-mdc-form-field-infix {
      border: none !important;
    }
    
    ::ng-deep .mat-mdc-raised-button.mat-mdc-button-disabled {
      background-color: rgba(156, 163, 175, 0.3) !important;
      color: rgba(255, 255, 255, 0.5) !important;
    }
  `]
})
export class ChatInputComponent {
  @Input() loading: boolean = false;
  @Input() error: string = '';
  @Output() sendMessage = new EventEmitter<string>();
  @ViewChild('messageInput') messageInput!: ElementRef<HTMLInputElement>;

  message: string = '';

  onSendMessage(): void {
    if (this.message.trim() && !this.loading) {
      this.sendMessage.emit(this.message.trim());
      this.message = '';
    }
  }

  focus(): void {
    if (this.messageInput) {
      this.messageInput.nativeElement.focus();
    }
  }

  clear(): void {
    this.message = '';
  }

  setMessage(text: string): void {
    this.message = text;
  }
}
