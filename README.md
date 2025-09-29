# Weather AI Assistant

A conversational weather application powered by AI that provides current weather conditions, forecasts, air quality data, and personalized advice. Built with Angular frontend and FastAPI backend.

## 🌟 Features

- **AI-Powered Weather Chat**: Conversational interface with Google Gemini AI
- **Current Weather & Forecasts**: Real-time weather data and 5-day forecasts
- **Historical Weather Context**: 7-day contextual weather patterns and trends
- **Air Quality Monitoring**: AQI data with health recommendations
- **Weather Knowledge Base**: Vector database with weather phenomena explanations and educational content
- **Session Management**: Persistent chat sessions with conversation history
- **Context-Aware Responses**: AI remembers previous conversations
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Live Demo**: Available at [https://weather-ai-assistant-ui.onrender.com/](https://weather-ai-assistant-ui.onrender.com/)

## 📋 Prerequisites

- **Node.js** (v18 or higher) - [Download](https://nodejs.org/)
- **Python** (v3.11 or higher) - [Download](https://python.org/)
- **Git** - [Download](https://git-scm.com/)

### Required API Keys
- **Google API Key** - For Gemini AI integration ([Get it here](https://makersuite.google.com/app/apikey))
- **OpenWeatherMap API Key** - For weather data ([Get it here](https://openweathermap.org/api))
- **Weaviate API Key** - For vector database knowledge base ([Get it here](https://console.weaviate.cloud/))
- **LangChain API Key** (Optional) - For tracing and monitoring ([Get it here](https://smith.langchain.com/))

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/MarkAPhillips/weather-ai-assistant.git
cd weather-ai-assistant
```

### 2. Backend Setup (FastAPI)

```bash
cd server
python -m venv venv

# Activate virtual environment
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
```

#### Environment Configuration
Create a `.env` file in the `server` directory:
```bash
GOOGLE_API_KEY=your_google_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
WEAVIATE_CLUSTER_URL=https://your-cluster-url.weaviate.cloud
WEAVIATE_API_KEY=your_weaviate_api_key_here
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

### 3. Frontend Setup (Angular)

```bash
cd client
npm install
npm start
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
│   ├── src/app/
│   │   ├── components/chat/         # Chat components
│   │   │   ├── air-quality-card/    # Air quality display
│   │   │   ├── chat-header/         # Chat header
│   │   │   ├── chat-input/          # Message input
│   │   │   ├── chat-message/        # Message display
│   │   │   ├── session-list/        # Session management
│   │   │   └── models/              # Chat data models
│   │   └── services/                # API services
│   └── environments/                # Environment configs
├── server/                          # FastAPI backend
│   ├── agents/                      # AI agents
│   │   └── weather_agent.py         # Main weather AI agent
│   ├── services/                    # Business logic services
│   │   ├── air_quality_service.py   # Air quality data
│   │   ├── weather_service.py       # Weather data
│   │   └── weaviate_service.py      # Knowledge base
│   ├── sessions/                    # Session management
│   │   └── session_manager.py       # Chat session handling
│   ├── models/                      # Data models
│   │   ├── air_quality.py          # Air quality models
│   │   ├── chat.py                 # Chat models
│   │   └── weather.py              # Weather models
│   ├── main.py                     # FastAPI application
│   └── requirements.txt            # Python dependencies
└── README.md
```

## 🚀 Deployment

### Render Deployment

The application is deployed on [Render](https://render.com/) with automatic CI/CD from GitHub.

#### Environment Variables
Set these in Render dashboard:
```
ENVIRONMENT=production
GOOGLE_API_KEY=your_google_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
WEAVIATE_CLUSTER_URL=https://your-cluster-url.weaviate.cloud
WEAVIATE_API_KEY=your_weaviate_api_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langchain_api_key
LANGCHAIN_PROJECT=weather-ai-assistant
```

**Note**: API keys are stored in Render environment variables, not GitHub secrets.

## 📚 API Documentation

### Endpoints

- `GET /api/health` - Health check
- `POST /api/chat/send` - Send message
- `GET /api/chat/sessions` - List sessions
- `GET /api/chat/sessions/{id}` - Get session
- `POST /api/chat/sessions` - Create session
- `DELETE /api/chat/sessions/{id}` - Delete session
- `DELETE /api/chat/sessions` - Delete all sessions

### Interactive API Docs
- **Local Development**: Visit `http://localhost:8000/docs` for Swagger UI documentation
- **Production**: API documentation is disabled for security reasons

## 🛠️ Troubleshooting

### Common Issues

#### Backend Issues
- **502 Bad Gateway**: Check API keys in environment variables
- **Import Errors**: Ensure virtual environment is activated and dependencies are installed
- **Port Conflicts**: Change port in `uvicorn` command
- **Weaviate Connection Issues**: Verify `WEAVIATE_CLUSTER_URL` and `WEAVIATE_API_KEY` are correct

#### Frontend Issues
- **Build Errors**: Check Node.js version (v18+)
- **API Connection**: Verify backend is running on port 8000

#### Weaviate Setup
- **Collection Creation**: Ensure your Weaviate API key has admin permissions
- **Vectorizer Issues**: The app uses keyword-based search as fallback if vectorizer is not configured
- **Knowledge Base**: The weather knowledge base is populated with sample data on first run

### Debug Commands

```bash
# Check backend health
curl http://localhost:8000/api/health

# Check frontend build
cd client && npm run build --configuration=production

# Check dependencies
cd server && source venv/bin/activate && pip list
cd client && npm list --depth=0
```

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
- **Weaviate** for vector database and knowledge base
- **Angular** for the frontend framework
- **FastAPI** for the backend framework
- **LangChain** for AI agent orchestration
- **Render** for free hosting

---

**Happy Weather Chatting! 🌤️**