import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { WeatherService, WeatherQuery, WeatherResponse, Location } from '../../services/weather.service';

@Component({
  selector: 'app-weather-assistant',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './weather-assistant.component.html',
})
export class WeatherAssistantComponent implements OnInit {
  query: string = '';
  city: string = '';
  response: string = '';
  loading: boolean = false;
  error: string = '';
  userLocation: Location | null = null;
  locationPermission: string = 'unknown';

  constructor(private weatherService: WeatherService) { }

  ngOnInit(): void {
    this.checkHealth();
  }

  checkHealth(): void {
    this.weatherService.getHealth().subscribe({
      next: (data) => console.log('Backend health:', data),
      error: (err) => console.error('Backend health check failed:', err)
    });
  }

  getCurrentLocation(): void {
    if (!navigator.geolocation) {
      this.error = 'Geolocation is not supported by this browser.';
      return;
    }

    this.loading = true;
    navigator.geolocation.getCurrentPosition(
      (position) => {
        this.userLocation = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        };
        this.locationPermission = 'granted';
        this.loading = false;
      },
      (error) => {
        this.locationPermission = 'denied';
        this.error = 'Unable to retrieve your location: ' + error.message;
        this.loading = false;
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000
      }
    );
  }

  onSubmit(): void {
    this.loading = true;
    this.error = '';

    const request: WeatherQuery = {
      query: this.query,
      city: this.city || undefined,
      userLocation: this.userLocation || undefined
    };

    this.weatherService.getWeatherAdvice(request).subscribe({
      next: (data: WeatherResponse) => {
        this.response = data.response;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to get weather advice: ' + err.message;
        this.loading = false;
      }
    });
  }
}
