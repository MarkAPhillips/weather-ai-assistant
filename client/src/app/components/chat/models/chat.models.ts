export interface ChatMessage {
  role: string;
  content: string;
  timestamp: string;
  message_id: string;
  image?: WeatherImage;
}

export interface WeatherImage {
  url: string;
  alt: string;
  photographer: string;
  photographer_url: string;
  query: string;
}

export interface ChatSession {
  session_id: string;
  messages: ChatMessage[];
  created_at: string;
  last_activity: string;
}

export interface ChatRequest {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  message_id: string;
  timestamp: string;
}

export interface SessionStats {
  total_sessions: number;
  active_sessions: number;
  expired_sessions: number;
}

export interface HealthResponse {
  status: string;
  service: string;
  timestamp: string;
  components?: {
    weather_agent: string;
    environment: string;
  };
}

export interface AirQualityData {
  aqi?: number;
  pm25?: number;
  pm10?: number;
  o3?: number;
  no2?: number;
  so2?: number;
  co?: number;
  location?: string;
  timestamp?: string;
  health_recommendations?: string[];
}

export interface WeatherDataWithAirQuality {
  city: string;
  country: string;
  temperature: number;
  condition: string;
  humidity: number;
  wind_speed: number;
  wind_direction: string;
  pressure: number;
  visibility: number;
  uv_index?: number;
  air_quality?: AirQualityData;
}
