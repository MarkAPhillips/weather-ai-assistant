# Weather AI Assistant

A conversational weather application powered by AI that provides current weather conditions, forecasts, air quality data, and personalized advice. Built with Angular frontend and FastAPI backend, featuring session management, context-aware conversations, and a modern glassmorphism UI.

## 🌟 Features

### Core Functionality
- **AI-Powered Weather Chat**: Conversational interface with Google Gemini AI
- **Current Weather & Forecasts**: Real-time weather data and 5-day forecasts
- **Air Quality Monitoring**: AQI data with health recommendations
- **Session Management**: Persistent chat sessions with conversation history
- **Context-Aware Responses**: AI remembers previous conversations
- **Multi-turn Conversations**: Follow-up questions and conversation continuity

### User Experience
- **Typewriter Effect**: Smooth, character-by-character response display
- **Clickable Example Prompts**: Quick-start conversation starters
- **Glassmorphism UI**: Modern dark theme with frosted glass effects
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Material Design Integration**: Angular Material components
- **Toast Notifications**: Themed notifications for user feedback

### Technical Features
- **Component Architecture**: Modular Angular components for maintainability
- **Standalone Components**: Modern Angular architecture
- **Tailwind CSS**: Utility-first styling framework
- **Free Hosting**: Deployed on Render with GitHub Actions CI/CD
- **Comprehensive Testing**: Unit tests for components and services
- **Error Handling**: Graceful error handling and user feedback

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
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   └── chat/            # Chat system components
│   │   │   │       ├── air-quality-card/     # Air quality display
│   │   │   │       │   ├── air-quality-card.component.ts
│   │   │   │       │   └── air-quality-card.component.spec.ts
│   │   │   │       ├── chat-header/         # Chat header component
│   │   │   │       │   ├── chat-header.component.ts
│   │   │   │       │   └── chat-header.component.spec.ts
│   │   │   │       ├── chat-input/           # Message input component
│   │   │   │       │   ├── chat-input.component.ts
│   │   │   │       │   └── chat-input.component.spec.ts
│   │   │   │       ├── chat-message/        # Individual message component
│   │   │   │       │   ├── chat-message.component.ts
│   │   │   │       │   ├── chat-message.component.html
│   │   │   │       │   └── chat-message.component.spec.ts
│   │   │   │       ├── session-list/       # Session management component
│   │   │   │       │   ├── session-list.component.ts
│   │   │   │       │   ├── session-list.component.html
│   │   │   │       │   └── session-list.component.spec.ts
│   │   │   │       ├── models/             # TypeScript interfaces
│   │   │   │       │   └── chat.models.ts
│   │   │   │       ├── chat.component.ts   # Main chat orchestrator
│   │   │   │       ├── chat.component.html # Main chat template
│   │   │   │       └── chat.component.spec.ts
│   │   │   ├── services/
│   │   │   │   ├── weather.service.ts       # API service
│   │   │   │   └── weather.service.spec.ts
│   │   │   ├── app.component.ts             # Root component
│   │   │   ├── app.config.ts                # App configuration
│   │   │   └── app.routes.ts                # Routing configuration
│   │   ├── environments/                    # Environment configs
│   │   │   ├── environment.ts               # Development config
│   │   │   └── environment.prod.ts          # Production config
│   │   ├── index.html                       # Main HTML file
│   │   ├── index.css                        # Global styles
│   │   └── main.ts                          # App bootstrap
│   ├── package.json                         # Dependencies
│   ├── angular.json                         # Angular configuration
│   ├── tailwind.config.js                   # Tailwind CSS config
│   └── tsconfig.json                        # TypeScript config
├── server/                          # FastAPI backend
│   ├── main.py                      # FastAPI application
│   ├── weather_agent.py             # AI weather agent with LangChain
│   ├── air_quality_service.py       # Air quality data service
│   ├── session_manager.py            # Chat session management
│   ├── models.py                     # Pydantic data models
│   ├── test_main.py                  # Backend tests
│   ├── requirements.txt              # Python dependencies
│   └── venv/                         # Virtual environment
├── .github/workflows/                # CI/CD pipelines
│   ├── api-build-and-deploy.yml      # Backend deployment
│   └── ui-build-and-deploy.yml       # Frontend deployment
├── Dockerfile                        # Docker configuration
└── README.md                         # This file
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

#### Frontend Linting
```bash
cd client
npm run lint
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

### Free Hosting Options

#### Option 1: Render (Recommended)
- **Backend**: Web service with Docker
- **Frontend**: Static site
- **Cost**: Free tier available
- **Setup**: Automatic from GitHub

#### Option 2: Railway
- **Backend**: Web service
- **Frontend**: Static site
- **Cost**: Free tier available
- **Setup**: Connect GitHub repository

#### Option 3: Fly.io
- **Backend**: Web service
- **Frontend**: Static site
- **Cost**: Free tier available
- **Setup**: CLI-based deployment

### Render Deployment (Current Setup)

#### 1. Backend Deployment
- **Service Type**: Web Service
- **Build Command**: `pip install -r server/requirements.txt`
- **Start Command**: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`
- **Health Check**: `/api/health`

#### 2. Frontend Deployment
- **Service Type**: Static Site
- **Build Command**: `cd client && npm install && npm run build --configuration=production`
- **Publish Directory**: `client/dist/client/browser`

#### 3. Environment Variables
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
- ✅ Run tests and linting
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

#### Root Endpoint
```
GET /                            # Basic connectivity test
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
Visit `http://localhost:8000/docs` for Swagger UI documentation.

## 🎨 UI Components & Features

### Component Architecture
The frontend uses a modular component architecture with standalone Angular components:

#### Main Components
- **`ChatComponent`**: Main orchestrator managing chat state and session handling
- **`ChatMessageComponent`**: Displays individual messages with typewriter effect and air quality cards
- **`ChatInputComponent`**: Handles message input with Material Design form fields
- **`SessionListComponent`**: Manages session display, deletion, and cleanup
- **`AirQualityCardComponent`**: Displays detailed air quality information with health recommendations

#### Key Features
- **Glassmorphism Design**: Dark theme with frosted glass effects using `backdrop-blur`
- **Material Design Integration**: Angular Material components for consistent UI
- **Tailwind CSS**: Utility-first styling for responsive design
- **Typewriter Effect**: Smooth character-by-character message display
- **Clickable Examples**: Pre-defined weather prompts for quick conversation starts
- **Session Management**: Visual session list with cleanup and deletion options
- **Toast Notifications**: Themed notifications matching the glassmorphism design

### Styling System
- **Global Styles**: `src/index.css` with Tailwind imports and Material Design overrides
- **Component Styles**: Inline styles using Tailwind classes
- **Theme Colors**: Dark gradient backgrounds with purple/slate color scheme
- **Responsive Design**: Mobile-first approach with responsive breakpoints

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
- **Google Gemini** for AI capabilities and natural language processing
- **Angular** for the modern frontend framework
- **FastAPI** for the high-performance backend framework
- **LangChain** for AI agent orchestration and tool integration
- **Render** for free hosting and deployment
- **Tailwind CSS** for utility-first styling
- **Angular Material** for consistent UI components
- **GitHub Actions** for CI/CD automation

## 📞 Support

If you encounter any issues:
1. Check the [Troubleshooting](#-troubleshooting) section
2. Review the [GitHub Issues](https://github.com/yourusername/weather-ai-assistant/issues)
3. Create a new issue with detailed information

---

**Happy Weather Chatting! 🌤️**
