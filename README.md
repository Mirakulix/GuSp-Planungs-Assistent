# 🏕️ Pfadi AI Assistent

KI-gestützte Planungsplattform für Pfadfinderleiter:innen der Altersstufe Guides und Späher (10-13 Jahre) in Niederösterreich und Wien.

## 🎯 Projektziele

- **Vereinfachung des kreativen Planungsprozesses** durch intelligente Vorschläge und Automatisierung
- **Bereitstellung pädagogischer Unterstützung** mit altersgerechten Inhalten und bewährten Praktiken  
- **Automatisierung administrativer Aufgaben** zur Entlastung der Leiter:innen
- **Zentrale Wissensdatenbank** für Spiele, pädagogische Inhalte und Pfadfinderwissen

## 🏗️ Systemarchitektur

### Technology Stack

**Frontend:**
- React 19 + TypeScript
- Vite (Build Tool)
- Mantine UI (Component Library)
- Tanstack Query (State Management)

**Backend:**
- Python 3.11+ 
- FastAPI (Web Framework)
- SQLAlchemy (ORM)
- Azure OpenAI Service (AI/KI)
- Azure AI Search (Semantic Search)

**Infrastructure:**
- Docker & Docker Compose
- Redis (Caching & Session Management)
- Azure Services (Production)

## 🚀 Quick Start

### Voraussetzungen

- Docker & Docker Compose
- Git
- (Optional) Node.js 18+ und Python 3.11+ für lokale Entwicklung

### 1. Repository klonen

```bash
git clone <repository-url>
cd GuSp-Planungs-Assistent
```

### 2. Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
# Bearbeite .env mit deinen Azure-Credentials
```

### 3. Mit Docker starten

```bash
# Alle Services starten
docker-compose up --build

# Nur Backend starten
docker-compose up backend redis

# Nur Frontend starten  
docker-compose up frontend
```

### 4. Anwendung öffnen

- **Frontend:** http://localhost:3000
- **Backend API Docs:** http://localhost:8000/docs
- **Backend Health:** http://localhost:8000/health

## 💻 Lokale Entwicklung

### Backend Setup

```bash
cd backend

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt

# Server starten
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Dependencies installieren
npm install

# Development Server starten
npm run dev

# Build für Production
npm run build
```

## 📋 Verfügbare Features (MVP)

### ✅ Implementiert

- **🏗️ Basis-Setup:** Docker, FastAPI, React Frontend
- **💬 Chat Interface:** Grundlegendes Chat-UI mit Backend-Integration
- **🎯 Spiele-Suche:** Mock-API für Spielesuche mit Filtern
- **📅 Planungsansätze:** Basis-Struktur für Heimstunden-Planung
- **🔧 Health Checks:** Monitoring und Status-Endpoints

### 🚧 In Entwicklung

- **🤖 Azure OpenAI Integration:** KI-gestützter Chatbot
- **🔍 Semantische Suche:** Azure AI Search Integration
- **🗄️ Datenbank Setup:** SQLAlchemy Modelle und Migration
- **📚 Wissensdatenbank:** RAG-System für Pfadfinderwissen

### 📋 Geplant

- **🏕️ Lagerplanung:** Erweiterte Planungstools für Lager
- **📧 Kommunikation:** E-Mail/WhatsApp Integration
- **👥 Anmeldungsverwaltung:** Event-Management
- **🏆 Abzeichenverwaltung:** Fortschrittstracking

## 🔧 Konfiguration

### Umgebungsvariablen

Wichtige Konfigurationswerte in `.env`:

```bash
# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4

# Azure AI Search  
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-key

# Database
DATABASE_URL=sqlite:///./pfadi_assistant.db

# Redis
REDIS_URL=redis://localhost:6379
```

### Feature Flags

Features können in `backend/app/core/config.py` aktiviert/deaktiviert werden:

```python
ENABLE_CHATBOT = True
ENABLE_GAME_SEARCH = True  
ENABLE_PLANNING = True
ENABLE_CAMP_PLANNING = False  # Coming soon
ENABLE_COMMUNICATION = False  # Coming soon
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

```bash
# Mit Docker Compose
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📚 API Dokumentation

Die vollständige API-Dokumentation ist verfügbar unter:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Wichtige Endpoints

```
GET  /api/v1/health           # System Health Check
POST /api/v1/chat             # Chat with AI Assistant  
GET  /api/v1/games/search     # Search Games
POST /api/v1/planning/heimstunde  # Create Activity Plan
```

## 🚢 Deployment

### Lokales Production Build

```bash
# Production Build
docker-compose -f docker-compose.prod.yml up --build
```

### Azure Deployment

Siehe `docs/DEPLOYMENT.md` für detaillierte Azure-Deployment-Anweisungen.

## 🤝 Contributing

1. Fork das Repository
2. Erstelle einen Feature Branch (`git checkout -b feature/amazing-feature`)
3. Committe deine Änderungen (`git commit -m 'Add amazing feature'`)
4. Push zum Branch (`git push origin feature/amazing-feature`)
5. Öffne eine Pull Request

### Code Style

- **Backend:** Black, isort, flake8, mypy
- **Frontend:** ESLint, Prettier

```bash
# Backend Code Formatting
cd backend
black .
isort .
flake8 .
mypy .

# Frontend Code Formatting  
cd frontend
npm run lint
npm run format
```

## 📄 Lizenz

Dieses Projekt steht unter der GPL v3 Lizenz. Siehe [LICENSE](LICENSE) für Details.

## 📞 Support

- **Issues:** GitHub Issues für Bug Reports und Feature Requests
- **Diskussionen:** GitHub Discussions für allgemeine Fragen
- **Dokumentation:** [Technische Spezifikation](TECHNICAL_SPECIFICATION.md)

## 🏗️ Projektstruktur

```
GuSp-Planungs-Assistent/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── api/               # API Endpoints
│   │   ├── core/              # Core Configuration
│   │   ├── models/            # Database Models
│   │   ├── services/          # Business Logic
│   │   └── utils/             # Utilities
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # React Components
│   │   ├── pages/             # Page Components
│   │   ├── hooks/             # Custom Hooks
│   │   └── utils/             # Utilities
│   ├── package.json
│   └── Dockerfile
├── data/                       # Data Directory
│   ├── local/                 # Local Files
│   └── google_drive/          # Google Drive Sync
├── docs/                       # Documentation
├── tests/                      # Test Files
├── docker-compose.yml          # Development Setup
├── .env.example               # Environment Template
└── README.md                  # This File
```

---

**Gut Pfad!** 🔥 Entwickelt mit ❤️ für die Pfadfinderbewegung