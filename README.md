# Weather AI Assistant

A conversational weather application powered by AI that provides current weather conditions, forecasts, air quality data, and personalized advice. Built with Angular frontend and FastAPI backend.

## 🌟 Features

- **AI-Powered Weather Chat**: Conversational interface with Google Gemini AI
- **Current Weather & Forecasts**: Real-time weather data and 5-day forecasts
- **Air Quality Monitoring**: AQI data with health recommendations
- **Session Management**: Persistent chat sessions with conversation history
- **Context-Aware Responses**: AI remembers previous conversations
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Live Demo**: Available at [https://weather-ai-assistant-ui.onrender.com/](https://weather-ai-assistant-ui.onrender.com/)

## 📋 Prerequisites

### Required Software
- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.11 or higher) - [Download](https://python.org/)
- **Git** - [Download](https://git-scm.com/)
- **npm** (comes with Node.js)

### Required API Keys
- **Google API Key** - For Gemini AI integration
  - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
  - Create a new API key
- **OpenWeatherMap API Key** - For weather data
  - Go to [OpenWeatherMap](https://openweathermap.org/api)
  - Sign up and get your free API key
- **LangChain API Key** (Optional) - For tracing and monitoring
  - Go to [LangSmith](https://smith.langchain.com/)
  - Create a free account and get your API key
  - **Benefits**: Debug AI responses, monitor performance, track conversation flows

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/MarkAPhillips/weather-ai-assistant.git
cd weather-ai-assistant
```

### 2. Backend Setup (FastAPI)

#### Create Virtual Environment
```bash
cd server
python -m venv venv
```

#### Activate Virtual Environment
```bash
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

#### Install Dependencies
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the `server` directory:
```bash
# server/.env
GOOGLE_API_KEY=your_google_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here

# Optional: LangChain tracing (for monitoring and debugging)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langchain_api_key_here
LANGCHAIN_PROJECT=weather-ai-assistant
```

#### Run the Backend
```bash
# Make sure virtual environment is activated
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

#### Test the Backend
```bash
# Health check
curl http://localhost:8000/api/health

# API documentation
open http://localhost:8000/docs
```

### 3. Frontend Setup (Angular)

#### Install Dependencies
```bash
cd client
npm install
```

#### Environment Configuration
The frontend automatically uses the correct environment:
- **Development**: `src/environments/environment.ts` (localhost:8000)
- **Production**: `src/environments/environment.prod.ts` (Render URL)

#### Run the Frontend
```bash
# From the client directory
npm start
# or
ng serve
```

The application will be available at: `http://localhost:4200`

### 4. Verify Everything Works

1. **Backend Health**: Visit `http://localhost:8000/api/health`
2. **Frontend**: Visit `http://localhost:4200`
3. **Test Chat**: Send a message like "What's the weather in London?"

## 🏗️ Project Structure

```
weather-ai-assistant/
├── client/                          # Angular frontend
│   ├── src/app/components/chat/     # Chat components
│   │   ├── air-quality-card.component.ts
│   │   ├── chat-header.component.ts
│   │   ├── chat-input.component.ts
│   │   ├── chat-message.component.ts
│   │   ├── chat.component.ts
│   │   ├── session-list.component.ts
│   │   └── models/chat.models.ts
│   ├── src/app/services/
│   │   └── weather.service.ts
│   ├── src/environments/
│   │   ├── environment.ts
│   │   └── environment.prod.ts
│   ├── package.json
│   └── angular.json
├── server/                          # FastAPI backend
│   ├── main.py                      # FastAPI application
│   ├── weather_agent.py             # AI weather agent
│   ├── air_quality_service.py       # Air quality service
│   ├── session_manager.py            # Session management
│   ├── models.py                     # Data models
│   ├── test_main.py                  # Tests
│   └── requirements.txt
├── .github/workflows/               # CI/CD
│   ├── api-build-and-deploy.yml
│   └── ui-build-and-deploy.yml
└── README.md
```

## 🔧 Development

### Running Tests

#### Backend Tests
```bash
cd server
python -m pytest test_main.py -v
```

#### Frontend Tests
```bash
cd client
npm run test
```

### Code Quality

#### Backend Linting
```bash
cd server
pip install flake8
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Building for Production

#### Backend
```bash
cd server
# No build step needed - Python runs directly
```

#### Frontend
```bash
cd client
npm run build --configuration=production
# Output: dist/client/browser/
```

## 🚀 Deployment

### Render Deployment

The application is deployed on [Render](https://render.com/) with automatic CI/CD from GitHub:

#### Backend Deployment
- **Service Type**: Web Service
- **Build Command**: `pip install -r server/requirements.txt`
- **Start Command**: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`
- **Health Check**: `/api/health`

#### Frontend Deployment
- **Service Type**: Static Site
- **Build Command**: `cd client && npm install && npm run build --configuration=production`
- **Publish Directory**: `client/dist/client/browser`

#### Environment Variables
Set these in Render dashboard:
```
GOOGLE_API_KEY=your_google_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=weather-ai-assistant
```

### GitHub Actions CI/CD

The project includes automated CI/CD pipelines:

#### Backend Pipeline (`.github/workflows/api-build-and-deploy.yml`)
- ✅ Run tests and linting
- ✅ Deploy to Render on main branch push
- ✅ Environment variable validation

#### Frontend Pipeline (`.github/workflows/ui-build-and-deploy.yml`)
- ✅ Run tests
- ✅ Build production artifacts
- ✅ Deploy to Render on main branch push

#### Required GitHub Secrets
```
GOOGLE_API_KEY=your_google_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
LANGCHAIN_API_KEY=your_langchain_api_key
RENDER_API_KEY=your_render_api_key
RENDER_API_SERVICE_ID=your_backend_service_id
RENDER_UI_SERVICE_ID=your_frontend_service_id
```

## 🛠️ Troubleshooting

### Common Issues

#### Backend Issues
- **502 Bad Gateway**: Check API keys in environment variables
- **Import Errors**: Ensure virtual environment is activated and dependencies are installed
- **Port Conflicts**: Change port in `uvicorn` command
- **Command Not Found**: Make sure virtual environment is activated (`source venv/bin/activate`)

#### Frontend Issues
- **Build Errors**: Check Node.js version (v18+)
- **API Connection**: Verify backend is running on port 8000
- **Environment**: Check `environment.ts` vs `environment.prod.ts`

#### Deployment Issues
- **Render 401**: Check API key and service ID
- **Build Failures**: Check GitHub Actions logs
- **Environment Variables**: Verify all secrets are set

### Debug Commands

#### Check Backend Health
```bash
curl http://localhost:8000/api/health
```

#### Check Frontend Build
```bash
cd client
npm run build --configuration=production
ls -la dist/client/browser/
```

#### Check Dependencies
```bash
# Backend (make sure venv is activated)
cd server
source venv/bin/activate  # On macOS/Linux
pip list

# Frontend
cd client
npm list --depth=0
```

## 📚 API Documentation

### Endpoints

#### Health Check
```
GET /api/health
```

#### Chat Endpoints
```
POST /api/chat/send              # Send message
GET  /api/chat/sessions          # List sessions
GET  /api/chat/sessions/{id}     # Get session
POST /api/chat/sessions          # Create session
DELETE /api/chat/sessions/{id}    # Delete session
DELETE /api/chat/sessions         # Delete all sessions
GET  /api/chat/stats             # Session statistics
POST /api/chat/cleanup           # Cleanup expired sessions
```

### Data Models

#### ChatMessage
```typescript
{
  role: 'user' | 'assistant',
  content: string,
  timestamp: string
}
```

#### ChatSession
```typescript
{
  session_id: string,
  messages: ChatMessage[],
  created_at: string,
  last_activity: string
}
```

#### AirQualityData
```typescript
{
  aqi?: number,
  pm25?: number,
  pm10?: number,
  o3?: number,
  no2?: number,
  so2?: number,
  co?: number,
  location?: string,
  timestamp?: string,
  health_recommendations?: string[]
}
```

### Interactive API Docs
- **Local Development**: Visit `http://localhost:8000/docs` for Swagger UI documentation
- **Live API**: Visit [https://weather-ai-assistant-zoon.onrender.com/docs](https://weather-ai-assistant-zoon.onrender.com/docs) for the deployed API documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `npm test` and `python -m pytest`
5. Commit changes: `git commit -m "Add feature"`
6. Push to branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenWeatherMap** for weather data and air quality APIs
- **Google Gemini** for AI capabilities
- **Angular** for the frontend framework
- **FastAPI** for the backend framework
- **LangChain** for AI agent orchestration
- **Render** for free hosting

## 📞 Support

If you encounter any issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [GitHub Issues](https://github.com/yourusername/weather-ai-assistant/issues)
3. Create a new issue with detailed information

---

**Happy Weather Chatting! 🌤️**
