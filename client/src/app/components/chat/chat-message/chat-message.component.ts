import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { ChatMessage, AirQualityData } from '../models/chat.models';
import { AirQualityCardComponent } from '../air-quality-card/air-quality-card.component';

@Component({
  selector: 'app-chat-message',
  standalone: true,
  imports: [CommonModule, MatIconModule, AirQualityCardComponent],
  templateUrl: './chat-message.component.html'
})
export class ChatMessageComponent {
  @Input({ required: true }) message!: ChatMessage;
  @Input() typewriterActive: boolean = false;
  @Input() isLastMessage: boolean = false;
  @Output() skipTypewriter = new EventEmitter<void>();

  get canSkipTypewriter(): boolean {
    return this.message.role === 'assistant' && 
           this.typewriterActive && 
           this.isLastMessage;
  }

  get showTypewriterCursor(): boolean {
    return this.canSkipTypewriter;
  }

  onMessageClick(): void {
    if (this.canSkipTypewriter) {
      this.skipTypewriter.emit();
    }
  }

  formatMessageContent(content: string): string {
    // Convert **text** to <strong>text</strong>
    return content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
  }

  formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch {
      return timestamp;
    }
  }

  hasAirQualityData(): boolean {
    // Only show air quality card if user specifically asked for detailed air quality info
    if (this.message.role !== 'assistant') {
      return false;
    }

    const content = this.message.content;
    const airQualityKeywords = [
      'Air Quality Index:',
      'Health Recommendations:',
      'PM2.5:',
      'PM10:',
      'detailed air quality',
      'air quality breakdown',
      'air quality details'
    ];

    // Check if the response contains detailed air quality data
    const hasDetailedAirQuality = airQualityKeywords.some(keyword => 
      content.toLowerCase().includes(keyword.toLowerCase())
    );

    return hasDetailedAirQuality && this.extractAirQualityData() !== null;
  }

  extractAirQualityData(): AirQualityData | null {
    if (this.message.role !== 'assistant') {
      return null;
    }

    const content = this.message.content;
    
    // Look for air quality patterns in the AI response
    // Backend format: "🟢 Air Quality Index: 25 (Good)"
    const aqiMatch = content.match(/Air Quality Index:\s*(\d+)/i);
    const pm25Match = content.match(/PM2\.5:\s*([\d.]+)/i);
    const pm10Match = content.match(/PM10:\s*([\d.]+)/i);
    const locationMatch = content.match(/Air Quality.*?for\s+([^:]+)/i) || 
                         content.match(/in\s+([^:]+).*?Air Quality/i);
    
    if (!aqiMatch) {
      return null;
    }

    const aqi = parseInt(aqiMatch[1]);
    const pm25 = pm25Match ? parseFloat(pm25Match[1]) : undefined;
    const pm10 = pm10Match ? parseFloat(pm10Match[1]) : undefined;
    const location = locationMatch ? locationMatch[1].trim() : undefined;

    // Extract health recommendations
    const healthRecommendations: string[] = [];
    
    // Look for "Health Recommendations:" section
    const recommendationsStart = content.indexOf('Health Recommendations:');
    if (recommendationsStart !== -1) {
      const recommendationsSection = content.substring(recommendationsStart);
      const lines = recommendationsSection.split('\n');
      
      for (const line of lines) {
        // Look for lines that start with "- " (dash followed by space)
        if (line.trim().startsWith('- ')) {
          const cleanLine = line.replace(/^-\s+/, '').trim();
          if (cleanLine && cleanLine.length > 5) {
            healthRecommendations.push(cleanLine);
          }
        }
      }
    }

    return {
      aqi,
      pm25,
      pm10,
      location,
      timestamp: this.message.timestamp,
      health_recommendations: healthRecommendations.length > 0 ? healthRecommendations : undefined
    };
  }
}
