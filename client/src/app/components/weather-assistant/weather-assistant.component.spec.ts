import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WeatherAssistantComponent } from './weather-assistant.component';

describe('WeatherAssistantComponent', () => {
  let component: WeatherAssistantComponent;
  let fixture: ComponentFixture<WeatherAssistantComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WeatherAssistantComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WeatherAssistantComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
