# 🚀 Wesza Platform - Complete Deployment Guide

## Overview
This guide walks you through deploying the Wesza Platform to your $6 DigitalOcean droplet, including backing up your existing application.

---

## 📋 Prerequisites

Before starting, ensure you have:
- ✅ DigitalOcean $6 droplet (Ubuntu 20.04/22.04)
- ✅ SSH access to your droplet
- ✅ Domain name pointing to your droplet IP (optional but recommended)
- ✅ Supabase account (free tier)
- ✅ Groq API key
- ✅ DigitalOcean Spaces account (for file storage)

---

## 🔧 Step-by-Step Deployment

### Method 1: Automated Deployment (Recommended)

#### 1. Upload Deployment Script to Your Droplet

From your **local machine**, run:

```bash
# Navigate to your Wesza project folder
cd /path/to/wesza

# Copy the deployment script to your droplet
scp infrastructure/deploy-to-droplet.sh root@YOUR_DROPLET_IP:/tmp/deploy.sh

# SSH into your droplet
ssh root@YOUR_DROPLET_IP
```

#### 2. Make Script Executable and Run

```bash
# Make the script executable
chmod +x /tmp/deploy.sh

# Run the deployment script
/tmp/deploy.sh
```

The script will automatically:
- ✅ Backup your existing `/opt/wesza` folder
- ✅ Create a 4GB swap file (critical for $6 droplets)
- ✅ Install Docker and Docker Compose
- ✅ Set up the application structure
- ✅ Build and start all containers

#### 3. Configure Environment Variables

After the script runs, you'll need to configure your `.env` file:

```bash
cd /opt/wesza
cp .env.example .env
nano .env
```

Fill in your credentials:

```env
# === BACKEND ===
ENV=production
PORT=8000

# Database (Supabase)
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[your-anon-key]

# Authentication
SECRET_KEY=generate-a-random-32-character-string-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI (Groq)
GROQ_API_KEY=gsk_your-groq-api-key-here

# Storage (DigitalOcean Spaces)
SPACES_KEY=your-do-spaces-key
SPACES_SECRET=your-do-spaces-secret
SPACES_REGION=nyc3
SPACES_BUCKET_NAME=wesza-apps
SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com

# Queue (Redis)
REDIS_URL=redis://localhost:6379/0

# Logging
LOG_LEVEL=INFO

# === FRONTEND ===
VITE_API_BASE_URL=https://wesza.online/api/v1
```

**Save and exit** (`Ctrl+X`, then `Y`, then `Enter`)

#### 4. Restart Services with New Configuration

```bash
cd /opt/wesza
docker compose down
docker compose up -d --build
```

---

### Method 2: Manual Deployment

If you prefer manual control:

#### 1. SSH into Your Droplet

```bash
ssh root@YOUR_DROPLET_IP
```

#### 2. Backup Existing Application

```bash
# Create backup directory
mkdir -p /opt/backups/wesza-$(date +%Y%m%d-%H%M%S)

# Backup existing wesza folder if it exists
if [ -d /opt/wesza ]; then
    cp -r /opt/wesza /opt/backups/wesza-$(date +%Y%m%d-%H%M%S)/
    echo "✓ Backup created"
fi
```

#### 3. Create Swap File (Critical for $6 Droplets)

```bash
# Create 4GB swap file
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Make it permanent
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# Verify
swapon --show
```

#### 4. Install Docker

```bash
# Download and run Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Add user to docker group
usermod -aG docker $USER
newgrp docker
```

#### 5. Install Docker Compose Plugin

```bash
apt update
apt install -y docker-compose-plugin
```

#### 6. Clone or Upload Wesza Code

**Option A: Git Clone**
```bash
mkdir -p /opt/wesza
cd /opt/wesza
git clone YOUR_GIT_REPO_URL .
git checkout main
```

**Option B: SCP from Local Machine**
```bash
# From your LOCAL machine (not the droplet):
scp -r backend/ frontend/ infrastructure/ root@YOUR_DROPLET_IP:/opt/wesza/
```

#### 7. Configure Environment Variables

```bash
cd /opt/wesza
cp .env.example .env
nano .env
# Fill in your credentials (see example above)
```

#### 8. Build and Deploy

```bash
cd /opt/wesza
docker compose up -d --build
```

#### 9. Verify Deployment

```bash
# Check container status
docker compose ps

# View logs
docker compose logs -f

# Test health endpoint
curl http://localhost:8000/api/v1/health
```

---

## 🔒 Setting Up HTTPS with Cloudflare Tunnel (Free)

### 1. Install Cloudflare Tunnel

```bash
docker run -d \
  --name cloudflared \
  --restart unless-stopped \
  cloudflare/cloudflared:latest \
  tunnel --no-autoupdate run
```

### 2. Configure Tunnel

Follow the interactive prompts:
```bash
docker exec -it cloudflared cloudflared tunnel login
docker exec -it cloudflared cloudflared tunnel create wesza-tunnel
```

### 3. Route Traffic

Configure Cloudflare to route `wesza.online` to your tunnel:
```bash
docker exec -it cloudflared cloudflared tunnel route dns wesza-tunnel wesza.online
```

---

## 📊 Monitoring and Maintenance

### Check Service Status

```bash
cd /opt/wesza
docker compose ps
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### Restart Services

```bash
docker compose restart
```

### Update Application

```bash
cd /opt/wesza
git pull origin main
docker compose pull
docker compose up -d --build
```

### Backup Database

```bash
# Export Supabase data via their dashboard
# Or use pg_dump if you have direct DB access
```

### Resource Monitoring

```bash
# Check RAM usage
free -h

# Check disk space
df -h

# Check CPU usage
top
```

---

## 🐛 Troubleshooting

### Issue: Containers Keep Crashing

**Solution:** Check logs and increase swap
```bash
docker compose logs backend
# If OOM (Out of Memory), increase swap:
swapoff /swapfile
fallocate -l 6G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
```

### Issue: Port Already in Use

**Solution:** Change port in docker-compose.yml
```yaml
ports:
  - "8080:8000"  # Change 8000 to 8080
```

### Issue: Can't Access Frontend

**Solution:** Check firewall rules
```bash
# Allow HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw enable
```

### Issue: Database Connection Failed

**Solution:** Verify Supabase credentials
```bash
# Test connection from droplet
docker compose exec backend bash
# Then inside container:
python -c "from sqlalchemy import create_engine; engine = create_engine('YOUR_DATABASE_URL'); engine.connect()"
```

---

## 📈 Performance Optimization for $6 Droplet

### 1. Limit Container Resources

Edit `docker-compose.yml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
  
  frontend:
    deploy:
      resources:
        limits:
          memory: 256M
```

### 2. Enable Docker Build Cache

```bash
export DOCKER_BUILDKIT=1
```

### 3. Use Multi-stage Builds

Already configured in Dockerfiles to reduce image size.

### 4. Schedule Regular Restarts

Add to crontab:
```bash
crontab -e

# Add this line to restart weekly (Sunday at 3 AM)
0 3 * * 0 cd /opt/wesza && docker compose restart
```

---

## 🎯 Post-Deployment Checklist

- [ ] Health endpoint responds: `curl http://YOUR_IP:8000/api/v1/health`
- [ ] Frontend loads in browser
- [ ] User registration works
- [ ] AI app generation works (test with a simple prompt)
- [ ] Generated PWAs are accessible
- [ ] HTTPS is working (if using Cloudflare)
- [ ] Backups are scheduled
- [ ] Monitoring is set up
- [ ] Firewall is configured
- [ ] Swap file is active (`swapon --show`)

---

## 📞 Quick Reference Commands

```bash
# Navigate to Wesza directory
cd /opt/wesza

# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart services
docker compose restart

# View real-time logs
docker compose logs -f

# Rebuild after code changes
docker compose build --no-cache && docker compose up -d

# Access backend shell
docker compose exec backend bash

# Access frontend shell
docker compose exec frontend sh

# Check resource usage
docker stats

# Clean up unused images
docker image prune -a

# Backup current state
tar -czf wesza-backup-$(date +%Y%m%d).tar.gz /opt/wesza
```

---

## 💰 Estimated Monthly Costs

| Service | Cost |
|---------|------|
| DigitalOcean Droplet ($6) | $6/month |
| Supabase (Free Tier) | $0/month |
| Groq API (Free Tier) | $0/month |
| DigitalOcean Spaces (250GB free) | $0/month |
| Cloudflare Tunnel | $0/month |
| **Total** | **$6/month** |

*Note: Costs may increase with usage beyond free tiers*

---

## 🎉 Success!

Your Wesza Platform is now live on your $6 DigitalOcean droplet!

**Access Points:**
- Frontend: `http://YOUR_DROPLET_IP` or `https://wesza.online`
- Backend API: `http://YOUR_DROPLET_IP:8000/api/v1`
- Health Check: `http://YOUR_DROPLET_IP:8000/api/v1/health`

**Next Steps:**
1. Test user registration and login
2. Generate your first app with AI
3. Share with your team!

For support, check the logs or refer to the documentation.

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Supabase Docs](https://supabase.com/docs)
- [Groq API Docs](https://console.groq.com/docs)
- [DigitalOcean Community Tutorials](https://www.digitalocean.com/community)
