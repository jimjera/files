# 🚀 Wesza Platform

**AI-powered no-code mobile app platform that generates offline-capable PWAs from natural language prompts.**

## Overview

Wesza enables small businesses, freelancers, and field teams to create custom mobile apps without coding. Simply describe what you need in natural language, and our AI generates a complete Progressive Web App (PWA) that works offline.

### Key Features

- ✅ **Visual Prompt Designer** - Text + drag-drop UI builder
- ✅ **AI Intent Classification** - Automatic vertical/use-case detection  
- ✅ **Template Generator** - JSON schema output
- ✅ **Code Generator** - React PWA with service worker for offline support
- ✅ **User Authentication** - Email/password + JWT tokens
- ✅ **App Deployment** - Upload to CDN, return unique URL
- ✅ **Basic Analytics** - Track app usage
- ✅ **Offline Sync Engine** - Local storage + background sync

### Technology Stack

**Backend (Python)**
- FastAPI 0.109.0 - Async, auto-docs, type-safe
- PostgreSQL (via Supabase) - Free tier, real-time, auth built-in
- SQLAlchemy 2.0+ - Type-safe queries, async support
- python-jose + passlib - JWT + bcrypt password hashing
- Celery + Redis - Background tasks
- structlog - Structured JSON logs

**Frontend (React PWA)**
- React + TypeScript 18+ - Type-safe, component reuse
- Vite 5+ - Fast HMR, PWA plugin support
- Zustand 4+ - Lightweight state management
- Tailwind CSS + Headless UI - Rapid styling
- Workbox - Service worker generation

**AI Integration (Groq API)**
- `llama-3.1-8b-instant` - Fast intent classification
- `openai/gpt-oss-20b` - JSON config generation
- `llama-3.3-70b-versatile` - Complex app code generation

**Infrastructure**
- DigitalOcean Droplet ($6/mo) - App server
- Supabase (Free) - Database + Auth
- DigitalOcean Spaces (Free 250GB) - File storage
- Groq Cloud (Free Tier) - AI inference
- Cloudflare Tunnel (Free) - HTTPS

## Project Structure

```
wesza/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Pydantic settings
│   │   ├── database.py          # SQLAlchemy engine
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── app.py
│   │   │   └── template.py
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── auth.py
│   │   │   ├── app.py
│   │   │   └── ai.py
│   │   ├── api/v1/              # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── apps.py
│   │   │   └── ai.py
│   │   ├── services/            # Business logic
│   │   │   ├── auth.py
│   │   │   ├── ai_orchestrator.py
│   │   │   ├── app_generator.py
│   │   │   └── deployer.py
│   │   ├── middleware/          # Auth middleware
│   │   └── utils/               # Helpers
│   ├── tests/
│   ├── requirements.txt
│   ├── Dockerfile
│   └── docker-compose.yml
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── lib/
│   ├── public/
│   ├── vite.config.ts
│   └── package.json
├── infrastructure/
├── .env.example
└── README.md
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Supabase account (free)
- Groq API key (free)
- DigitalOcean account (for Spaces)

### Backend Setup

1. **Clone the repository**
```bash
cd wesza/backend
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp ../.env.example .env
# Edit .env with your credentials
```

5. **Run with Docker Compose**
```bash
docker-compose up -d
```

Or run locally:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Verify health check**
```bash
curl http://localhost:8000/api/v1/health
# Should return: {"status":"ok","version":"2.0"}
```

### Frontend Setup

1. **Navigate to frontend directory**
```bash
cd ../frontend
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
cp ../.env.example .env.local
# Edit VITE_API_BASE_URL if needed
```

4. **Start development server**
```bash
npm run dev
```

5. **Open browser**
```
http://localhost:5173
```

## API Documentation

Once running, access interactive API docs at:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

### Key Endpoints

**Authentication**
- `POST /api/v1/auth/register` - Create new account
- `POST /api/v1/auth/login` - Login and get JWT token

**Applications**
- `POST /api/v1/apps/` - Create new app
- `GET /api/v1/apps/` - List user's apps
- `GET /api/v1/apps/{id}` - Get specific app
- `PATCH /api/v1/apps/{id}` - Update app

**AI Generation**
- `POST /api/v1/ai/prompt` - Generate app from natural language
- `POST /api/v1/ai/classify` - Classify intent only

## Testing

### Backend Tests
```bash
cd backend
pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
```

## Deployment

### Deploy to $6 DigitalOcean Droplet

1. **Prepare droplet**
```bash
ssh root@your-droplet-ip

# Create swap file (prevent OOM crashes)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
```

2. **Deploy backend**
```bash
# From your local machine
scp -r backend/* root@droplet:/opt/wesza/
ssh root@droplet
cd /opt/wesza
docker-compose up -d --build
```

3. **Setup Cloudflare Tunnel (Free HTTPS)**
```bash
docker run cloudflare/cloudflared:latest tunnel --no-autoupdate run
# Follow prompts to authenticate and route domain
```

## Development Workflow

1. **Create feature branch**
```bash
git checkout -b feature/your-feature
```

2. **Make changes with tests**
```bash
# Write tests first (TDD)
# Implement feature
# Run tests
pytest
```

3. **Format code**
```bash
black app/
isort app/
```

4. **Commit and push**
```bash
git add .
git commit -m "feat: description"
git push origin feature/your-feature
```

## Environment Variables

See `.env.example` for all required variables:

**Backend**
- `DATABASE_URL` - PostgreSQL connection string
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase anon key
- `SECRET_KEY` - JWT signing key
- `GROQ_API_KEY` - Groq API key
- `SPACES_KEY` - DigitalOcean Spaces key
- `SPACES_SECRET` - DigitalOcean Spaces secret

**Frontend**
- `VITE_API_BASE_URL` - Backend API URL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- GitHub Issues: https://github.com/wesza/platform/issues
- Documentation: https://docs.wesza.online

---

**Built with ❤️ using FastAPI, React, and Groq AI**
