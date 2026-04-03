# 🚀 Quick Start: Deploy Wesza to Your $6 DigitalOcean Droplet

## ⚡ 3-Minute Quick Deploy

### Step 1: SSH into Your Droplet
```bash
ssh root@YOUR_DROPLET_IP
```

### Step 2: Backup Existing App (If Any)
```bash
# Download and run backup script
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/wesza/main/infrastructure/backup-existing.sh
chmod +x backup-existing.sh
./backup-existing.sh
```

### Step 3: Deploy Wesza
```bash
# Download deployment script
curl -O https://raw.githubusercontent.com/YOUR_USERNAME/wesza/main/infrastructure/deploy-to-droplet.sh
chmod +x deploy-to-droplet.sh
./deploy-to-droplet.sh
```

### Step 4: Configure Environment
```bash
cd /opt/wesza
cp .env.example .env
nano .env
# Fill in your credentials (see below)
```

### Step 5: Restart Services
```bash
docker compose down
docker compose up -d --build
```

**Done!** Access your app at `http://YOUR_DROPLET_IP`

---

## 🔑 Required Credentials

Before deploying, gather these:

### 1. Supabase (Database + Auth)
- Go to https://supabase.com
- Create a new project (free tier)
- Get credentials from Settings → API
- You need:
  - `DATABASE_URL`
  - `SUPABASE_URL`
  - `SUPABASE_KEY`

### 2. Groq API (AI Models)
- Go to https://console.groq.com
- Create API key (free tier available)
- You need:
  - `GROQ_API_KEY`

### 3. DigitalOcean Spaces (File Storage)
- Go to DigitalOcean → Spaces
- Create a Space (nyc3 region recommended)
- Generate access keys
- You need:
  - `SPACES_KEY`
  - `SPACES_SECRET`
  - `SPACES_BUCKET_NAME`

### 4. Secret Key (Generate Random)
```bash
# Run this to generate a secure random key
openssl rand -hex 32
```
Copy the output to `SECRET_KEY` in your `.env`

---

## 📝 Complete .env Example

```env
# === BACKEND ===
ENV=production
PORT=8000

# Database (Supabase)
DATABASE_URL=postgresql://postgres:your-password@db.xyzabc.supabase.co:5432/postgres
SUPABASE_URL=https://xyzabc.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Authentication
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI (Groq)
GROQ_API_KEY=gsk_your-groq-api-key-here

# Storage (DigitalOcean Spaces)
SPACES_KEY=YOUR_SPACES_KEY
SPACES_SECRET=YOUR_SPACES_SECRET
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

---

## 🔍 Verify Deployment

```bash
# Check if all containers are running
docker compose ps

# View logs
docker compose logs -f

# Test health endpoint
curl http://localhost:8000/api/v1/health

# Should return: {"status":"ok","version":"2.0"}
```

---

## 🌐 Set Up HTTPS (Free with Cloudflare)

### Option 1: Cloudflare Tunnel (Recommended)
```bash
docker run -d \
  --name cloudflared \
  --restart unless-stopped \
  cloudflare/cloudflared:latest \
  tunnel --no-autoupdate run
```

Follow the prompts to:
1. Authenticate with Cloudflare
2. Create a tunnel
3. Route `wesza.online` → your droplet

### Option 2: Cloudflare Proxy
1. Point your domain to droplet IP
2. Enable "Proxy" in Cloudflare DNS settings
3. SSL/TLS mode: "Full"

---

## 🛠️ Common Commands

```bash
# Navigate to app directory
cd /opt/wesza

# Start services
docker compose up -d

# Stop services
docker compose down

# Restart services
docker compose restart

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Rebuild after updates
git pull
docker compose build --no-cache
docker compose up -d

# Access backend shell
docker compose exec backend bash

# Check resource usage
docker stats

# Update Docker images
docker compose pull
docker compose up -d
```

---

## 🐛 Troubleshooting

### Containers Keep Crashing
**Problem:** Out of memory on $6 droplet  
**Solution:**
```bash
# Check swap is active
swapon --show

# If no swap, create it
fallocate -l 4G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### Can't Access Frontend
**Problem:** Firewall blocking port 80  
**Solution:**
```bash
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8000/tcp
ufw enable
```

### Database Connection Error
**Problem:** Wrong Supabase credentials  
**Solution:**
1. Double-check `DATABASE_URL` in `.env`
2. Test connection:
```bash
docker compose exec backend python -c "from app.database import engine; print(engine.connect())"
```

### Port Already in Use
**Problem:** Another service using port 80 or 8000  
**Solution:**
Edit `docker-compose.yml` and change ports:
```yaml
ports:
  - "8080:80"  # Instead of 80
  - "8001:8000"  # Instead of 8000
```

---

## 📊 Monitoring

### Check Resource Usage
```bash
# RAM and CPU
docker stats

# Disk space
df -h

# Memory
free -h
```

### View Logs
```bash
# Last 100 lines
docker compose logs --tail=100

# Real-time
docker compose logs -f

# Specific service
docker compose logs -f backend
```

### Health Checks
```bash
# Backend health
curl http://localhost:8000/api/v1/health

# Redis health
docker compose exec redis redis-cli ping

# Container status
docker compose ps
```

---

## 🔄 Updating Wesza

### Automatic Updates (Git)
```bash
cd /opt/wesza
git pull origin main
docker compose pull
docker compose up -d --build
```

### Manual Updates (SCP)
From your local machine:
```bash
scp -r backend/* root@YOUR_DROPLET_IP:/opt/wesza/backend/
scp -r frontend/* root@YOUR_DROPLET_IP:/opt/wesza/frontend/
```

Then on droplet:
```bash
cd /opt/wesza
docker compose build --no-cache
docker compose up -d
```

---

## 💾 Backup Strategy

### Automated Daily Backups
Add to crontab (`crontab -e`):
```bash
# Daily backup at 3 AM
0 3 * * * cd /opt && tar -czf wesza-backup-$(date +\%Y\%m\%d).tar.gz wesza
```

### Manual Backup
```bash
cd /opt
tar -czf wesza-backup-$(date +%Y%m%d).tar.gz wesza
```

### Restore from Backup
```bash
cd /opt
tar -xzf wesza-backup-20240101.tar.gz
cd wesza
docker compose up -d
```

---

## 🎯 Post-Deployment Checklist

- [ ] Health endpoint responds: `curl http://YOUR_IP:8000/api/v1/health`
- [ ] Frontend loads in browser
- [ ] User registration works
- [ ] Login works
- [ ] AI app generation works (test with "Create a time tracker")
- [ ] Generated PWA is accessible
- [ ] HTTPS is working (if configured)
- [ ] Swap file is active: `swapon --show`
- [ ] Firewall configured: `ufw status`
- [ ] Backups scheduled

---

## 📞 Support & Resources

### Documentation
- Full deployment guide: `infrastructure/DEPLOYMENT_GUIDE.md`
- README: `README.md`
- Environment setup: `.env.example`

### Useful Links
- [Docker Docs](https://docs.docker.com/)
- [Supabase Docs](https://supabase.com/docs)
- [Groq API Docs](https://console.groq.com/docs)
- [DigitalOcean Community](https://www.digitalocean.com/community)

### Logs Location
```bash
# Application logs
docker compose logs -f

# System logs
journalctl -u docker.service -f
```

---

## 💰 Cost Breakdown

| Service | Cost | Notes |
|---------|------|-------|
| DigitalOcean Droplet | $6/mo | 1GB RAM, 1 vCPU, 25GB SSD |
| Supabase | $0/mo | Free tier: 500MB DB, 50K MAU |
| Groq API | $0/mo | Free tier available |
| DigitalOcean Spaces | $0/mo | Free tier: 250GB storage |
| Cloudflare | $0/mo | Free HTTPS & CDN |
| **Total** | **$6/mo** | Can scale with usage |

---

## 🎉 Success!

Your Wesza Platform is now live! 

**Access Points:**
- 🌐 Frontend: `http://YOUR_DROPLET_IP`
- 🔌 API: `http://YOUR_DROPLET_IP:8000/api/v1`
- ❤️ Health: `http://YOUR_DROPLET_IP:8000/api/v1/health`

**Next Steps:**
1. ✅ Test user registration
2. ✅ Generate your first AI app
3. ✅ Share with your team!
4. ✅ Set up HTTPS with Cloudflare
5. ✅ Configure automated backups

Happy building! 🚀
