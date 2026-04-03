# Wesza Frontend - Production Deployment Guide

This guide explains how to deploy the Wesza frontend to wesza.online for public users.

## Quick Deploy

### Option 1: Using the deployment script (Recommended)

```bash
cd /workspace/wesza/infrastructure
./quick-deploy.sh
```

### Option 2: Manual Docker Compose

```bash
# Navigate to frontend directory
cd /workspace/wesza/frontend

# Build and start all services
docker compose up -d --build
```

## Architecture

The frontend is served via:
- **React + Vite**: Modern React application with fast builds
- **Nginx**: Production web server with reverse proxy
- **Docker**: Containerized deployment
- **PWA**: Progressive Web App capabilities for mobile installation

## File Structure

```
frontend/
├── src/
│   ├── main.tsx          # Entry point
│   ├── App.tsx           # Main app component with routing
│   ├── pages/            # Page components
│   │   ├── HomePage.tsx
│   │   ├── DashboardPage.tsx
│   │   ├── CreateAppPage.tsx
│   │   └── AppsListPage.tsx
│   ├── components/       # Reusable UI components
│   ├── hooks/           # Custom React hooks
│   ├── lib/             # Utilities and API clients
│   └── styles/          # CSS and Tailwind styles
├── public/              # Static assets
├── Dockerfile           # Multi-stage Docker build
├── nginx.conf           # Nginx configuration
├── docker-compose.yml   # Production orchestration
└── vite.config.ts       # Vite build configuration
```

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=https://wesza.online/api/v1
```

## Pages Overview

1. **HomePage** (`/`) - Landing page with hero section and features
2. **DashboardPage** (`/dashboard`) - User dashboard with stats
3. **CreateAppPage** (`/create-app`) - AI-powered app creation form
4. **AppsListPage** (`/my-apps`) - List of user's created apps

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Production Commands

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop all services
docker compose down

# Update and redeploy
docker compose pull && docker compose up -d
```

## HTTPS Setup (Required for Production)

For wesza.online, you need HTTPS. Options:

### Option A: Cloudflare Tunnel (Recommended)
```bash
docker run -d --name cloudflared --restart unless-stopped \
  cloudflare/cloudflared:latest tunnel --no-autoupdate run
```

### Option B: Nginx Proxy Manager
Deploy nginx-proxy-manager and configure SSL certificates.

### Option C: Certbot
Use certbot with nginx for Let's Encrypt certificates.

## Health Checks

- Frontend: `http://localhost/health`
- Backend API: `http://localhost:8000/api/v1/health`

## Monitoring

```bash
# Check container status
docker compose ps

# View resource usage
docker stats

# Access frontend logs
docker compose logs frontend

# Access backend logs
docker compose logs backend
```

## Troubleshooting

### Frontend not loading
1. Check if container is running: `docker compose ps`
2. View logs: `docker compose logs frontend`
3. Verify port 80 is not in use: `sudo lsof -i :80`

### API calls failing
1. Ensure backend is running: `docker compose ps backend`
2. Check VITE_API_BASE_URL in .env
3. Verify network connectivity between containers

### Build errors
1. Clear node_modules: `rm -rf node_modules && npm install`
2. Clear Vite cache: `rm -rf dist`
3. Rebuild: `docker compose build --no-cache`

## Next Steps

After deployment:
1. Configure DNS for wesza.online
2. Set up HTTPS/SSL
3. Connect to backend API
4. Test all pages and functionality
5. Monitor performance and errors
