import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatIconModule } from '@angular/material/icon';
import { AirQualityCardComponent } from './air-quality-card.component';
import { AirQualityData } from '../models/chat.models';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('AirQualityCardComponent', () => {
  let component: AirQualityCardComponent;
  let fixture: ComponentFixture<AirQualityCardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AirQualityCardComponent, MatIconModule, NoopAnimationsModule]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AirQualityCardComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('AQI Classification', () => {
    it('should classify good air quality correctly', () => {
      const goodAirQuality: AirQualityData = {
        aqi: 25,
        pm25: 6.2,
        pm10: 12.1,
        location: 'London, GB',
        timestamp: new Date().toISOString(),
        health_recommendations: ['Good air quality']
      };

      component.airQuality = goodAirQuality;
      fixture.detectChanges();

      expect(component.getAqiClass()).toBe('border-green-400/30 bg-green-500/5');
      expect(component.getAqiStatus()).toBe('Good');
      expect(component.getAqiIcon()).toBe('eco');
    });

    it('should classify moderate air quality correctly', () => {
      const moderateAirQuality: AirQualityData = {
        aqi: 75,
        pm25: 18.5,
        pm10: 25.3,
        location: 'Paris, FR',
        timestamp: new Date().toISOString(),
        health_recommendations: ['Moderate air quality']
      };

      component.airQuality = moderateAirQuality;
      fixture.detectChanges();

      expect(component.getAqiClass()).toBe('border-yellow-400/30 bg-yellow-500/5');
      expect(component.getAqiStatus()).toBe('Moderate');
      expect(component.getAqiIcon()).toBe('wb_sunny');
    });

    it('should classify unhealthy air quality correctly', () => {
      const unhealthyAirQuality: AirQualityData = {
        aqi: 175,
        pm25: 45.2,
        pm10: 67.8,
        location: 'Beijing, CN',
        timestamp: new Date().toISOString(),
        health_recommendations: ['Unhealthy air quality']
      };

      component.airQuality = unhealthyAirQuality;
      fixture.detectChanges();

      expect(component.getAqiClass()).toBe('border-red-400/30 bg-red-500/5');
      expect(component.getAqiStatus()).toBe('Unhealthy');
      expect(component.getAqiIcon()).toBe('error');
    });
  });

  describe('Pollutant Data', () => {
    it('should detect when pollutant data is available', () => {
      const airQualityWithPollutants: AirQualityData = {
        aqi: 50,
        pm25: 12.0,
        pm10: 20.0,
        o3: 45.0,
        no2: 25.0,
        location: 'Test City',
        timestamp: new Date().toISOString()
      };

      component.airQuality = airQualityWithPollutants;
      fixture.detectChanges();

      expect(component.hasPollutantData()).toBe(true);
    });

    it('should detect when no pollutant data is available', () => {
      const airQualityWithoutPollutants: AirQualityData = {
        aqi: 50,
        location: 'Test City',
        timestamp: new Date().toISOString()
      };

      component.airQuality = airQualityWithoutPollutants;
      fixture.detectChanges();

      expect(component.hasPollutantData()).toBe(false);
    });
  });

  describe('Health Recommendations', () => {
    it('should show appropriate recommendation icons for good air quality', () => {
      const goodAirQuality: AirQualityData = {
        aqi: 25,
        pm25: 6.2,
        location: 'Test City',
        timestamp: new Date().toISOString(),
        health_recommendations: ['Good air quality']
      };

      component.airQuality = goodAirQuality;
      fixture.detectChanges();

      expect(component.getRecommendationIcon()).toBe('check_circle');
    });

    it('should show appropriate recommendation icons for unhealthy air quality', () => {
      const unhealthyAirQuality: AirQualityData = {
        aqi: 175,
        pm25: 45.2,
        location: 'Test City',
        timestamp: new Date().toISOString(),
        health_recommendations: ['Unhealthy air quality']
      };

      component.airQuality = unhealthyAirQuality;
      fixture.detectChanges();

      expect(component.getRecommendationIcon()).toBe('error');
    });
  });

  describe('Timestamp Formatting', () => {
    it('should format valid timestamp correctly', () => {
      const testTimestamp = '2024-01-15T14:30:00Z';
      const formatted = component.formatTimestamp(testTimestamp);
      // Format is "15 Jan, 14:30" in en-GB locale
      expect(formatted).toMatch(/\d{1,2} \w{3}, \d{2}:\d{2}/);
    });

    it('should handle invalid timestamp gracefully', () => {
      const invalidTimestamp = 'invalid-date';
      const formatted = component.formatTimestamp(invalidTimestamp);
      
      expect(formatted).toBe('Recent');
    });
  });

  describe('Template Rendering', () => {
    it('should render air quality card with all sections', () => {
      const completeAirQuality: AirQualityData = {
        aqi: 75,
        pm25: 18.5,
        pm10: 25.3,
        o3: 45.0,
        no2: 20.0,
        location: 'Test City, Country',
        timestamp: new Date().toISOString(),
        health_recommendations: [
          'Air quality is moderate',
          'Sensitive individuals may experience minor discomfort'
        ]
      };

      component.airQuality = completeAirQuality;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      
      // Check header elements using data-testid selectors
      const statusElement = compiled.querySelector('[data-testid="aqi-status"]');
      expect(statusElement?.textContent).toContain('Moderate');
      const aqiValueElement = compiled.querySelector('[data-testid="aqi-value"]');
      expect(aqiValueElement?.textContent).toContain('75');
      
      // Check pollutants section - using data-testid selectors
      const pollutantItems = compiled.querySelectorAll('[data-testid="pollutants-grid"] > div');
      expect(pollutantItems.length).toBeGreaterThan(0);
      
      // Check recommendations section - using data-testid selectors
      const recommendationItems = compiled.querySelectorAll('[data-testid="recommendations-list"] > div');
      expect(recommendationItems.length).toBeGreaterThan(0);
      
      // Check timestamp - using data-testid selectors
      const timestampElement = compiled.querySelector('[data-testid="air-quality-timestamp"]');
      expect(timestampElement).toBeTruthy();
    });

    it('should apply correct CSS class based on AQI', () => {
      const goodAirQuality: AirQualityData = {
        aqi: 25,
        pm25: 6.2,
        location: 'Test City',
        timestamp: new Date().toISOString()
      };

      component.airQuality = goodAirQuality;
      fixture.detectChanges();

      const compiled = fixture.nativeElement;
      const cardElement = compiled.querySelector('[data-testid="air-quality-card"]');
      
      expect(cardElement?.className).toContain('border-green-400/30 bg-green-500/5');
    });
  });
});
