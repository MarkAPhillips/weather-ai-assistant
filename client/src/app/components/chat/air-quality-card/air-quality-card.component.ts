import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { AirQualityData } from '../models/chat.models';

@Component({
  selector: 'app-air-quality-card',
  standalone: true,
  imports: [CommonModule, MatIconModule],
  template: `
    <div class="backdrop-blur-xl bg-white/10 border border-white/20 rounded-2xl p-4 mt-3 shadow-2xl transition-all duration-300 ease-in-out hover:bg-white/15 hover:border-white/30 hover:shadow-2xl hover:-translate-y-0.5 max-w-sm" 
         [ngClass]="getAqiClass()">
      
      <!-- Header -->
      <div class="flex items-center justify-between mb-4">
        <div class="flex items-center gap-3">
          <mat-icon class="text-2xl">{{ getAqiIcon() }}</mat-icon>
          <div class="flex flex-col">
            <span class="text-lg font-semibold text-white">{{ getAqiStatus() }}</span>
            <span class="text-sm text-slate-300">AQI: {{ airQuality.aqi }}</span>
          </div>
        </div>
        <div class="flex items-center gap-1 text-xs text-slate-400" *ngIf="airQuality.location">
          <mat-icon class="text-sm">location_on</mat-icon>
          <span>{{ airQuality.location }}</span>
        </div>
      </div>

      <!-- Pollutants -->
      <div class="mb-4" *ngIf="hasPollutantData()">
        <div class="flex items-center gap-2 mb-2">
          <mat-icon class="text-sm text-slate-400">science</mat-icon>
          <span class="text-sm font-medium text-slate-300">Pollutants</span>
        </div>
        <div class="grid grid-cols-2 gap-2">
          <div class="flex justify-between items-center p-2 rounded-lg bg-white/5 border border-white/10" *ngIf="airQuality.pm25">
            <span class="text-xs font-medium text-slate-300">PM2.5</span>
            <span class="text-xs text-slate-400">{{ airQuality.pm25 | number:'1.1-1' }} μg/m³</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded-lg bg-white/5 border border-white/10" *ngIf="airQuality.pm10">
            <span class="text-xs font-medium text-slate-300">PM10</span>
            <span class="text-xs text-slate-400">{{ airQuality.pm10 | number:'1.1-1' }} μg/m³</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded-lg bg-white/5 border border-white/10" *ngIf="airQuality.o3">
            <span class="text-xs font-medium text-slate-300">O₃</span>
            <span class="text-xs text-slate-400">{{ airQuality.o3 | number:'1.1-1' }} μg/m³</span>
          </div>
          <div class="flex justify-between items-center p-2 rounded-lg bg-white/5 border border-white/10" *ngIf="airQuality.no2">
            <span class="text-xs font-medium text-slate-300">NO₂</span>
            <span class="text-xs text-slate-400">{{ airQuality.no2 | number:'1.1-1' }} μg/m³</span>
          </div>
        </div>
      </div>

      <!-- Health Recommendations -->
      <div class="mb-4" *ngIf="airQuality.health_recommendations && airQuality.health_recommendations.length > 0">
        <div class="flex items-center gap-2 mb-2">
          <mat-icon class="text-sm text-slate-400">health_and_safety</mat-icon>
          <span class="text-sm font-medium text-slate-300">Health Recommendations</span>
        </div>
        <div class="space-y-2">
          <div class="flex items-start gap-2 p-2 rounded-lg bg-white/5 border border-white/10" *ngFor="let rec of airQuality.health_recommendations">
            <mat-icon class="text-sm text-green-400 mt-0.5">{{ getRecommendationIcon() }}</mat-icon>
            <span class="text-sm text-slate-300 leading-relaxed">{{ rec }}</span>
          </div>
        </div>
      </div>

      <!-- Timestamp -->
      <div class="flex items-center gap-1 text-xs text-slate-500 pt-2 border-t border-white/10" *ngIf="airQuality.timestamp">
        <mat-icon class="text-xs">schedule</mat-icon>
        <span>{{ formatTimestamp(airQuality.timestamp) }}</span>
      </div>
    </div>
  `
})
export class AirQualityCardComponent {
  @Input() airQuality!: AirQualityData;

  getAqiClass(): string {
    if (!this.airQuality?.aqi) return '';
    
    const aqi = this.airQuality.aqi;
    if (aqi <= 50) return 'border-green-400/30 bg-green-500/5';
    if (aqi <= 100) return 'border-yellow-400/30 bg-yellow-500/5';
    if (aqi <= 150) return 'border-orange-400/30 bg-orange-500/5';
    if (aqi <= 200) return 'border-red-400/30 bg-red-500/5';
    if (aqi <= 300) return 'border-purple-400/30 bg-purple-500/5';
    return 'border-red-600/30 bg-red-600/5';
  }

  getAqiIcon(): string {
    if (!this.airQuality?.aqi) return 'air';
    
    const aqi = this.airQuality.aqi;
    if (aqi <= 50) return 'eco';
    if (aqi <= 100) return 'wb_sunny';
    if (aqi <= 150) return 'warning';
    if (aqi <= 200) return 'error';
    if (aqi <= 300) return 'dangerous';
    return 'report_problem';
  }

  getAqiStatus(): string {
    if (!this.airQuality?.aqi) return 'Unknown';
    
    const aqi = this.airQuality.aqi;
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Moderate';
    if (aqi <= 150) return 'Unhealthy for Sensitive Groups';
    if (aqi <= 200) return 'Unhealthy';
    if (aqi <= 300) return 'Very Unhealthy';
    return 'Hazardous';
  }

  hasPollutantData(): boolean {
    return !!(this.airQuality?.pm25 || this.airQuality?.pm10 || 
              this.airQuality?.o3 || this.airQuality?.no2);
  }

  getRecommendationIcon(): string {
    if (!this.airQuality?.aqi) return 'info';
    
    const aqi = this.airQuality.aqi;
    if (aqi <= 50) return 'check_circle';
    if (aqi <= 100) return 'info';
    if (aqi <= 150) return 'warning';
    if (aqi <= 200) return 'error';
    if (aqi <= 300) return 'dangerous';
    return 'report_problem';
  }

  formatTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      return date.toLocaleString('en-GB', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch {
      return 'Recent';
    }
  }
}