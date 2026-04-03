#!/bin/bash
# Wesza Platform - Complete Deployment Script for DigitalOcean $6 Droplet
# This script backs up existing app, sets up Docker, and deploys Wesza

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WESZA_DIR="/opt/wesza"
BACKUP_DIR="/opt/backups/wesza-$(date +%Y%m%d-%H%M%S)"
SWAP_SIZE="4G"

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Wesza Platform Deployment Script              ║${NC}"
echo -e "${BLUE}║        DigitalOcean $6 Droplet Setup                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to print status messages
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Step 1: Backup existing wesza folder if it exists
echo -e "${YELLOW}Step 1: Backing up existing Wesza installation...${NC}"
if [ -d "$WESZA_DIR" ]; then
    mkdir -p "$BACKUP_DIR"
    cp -r "$WESZA_DIR" "$BACKUP_DIR/"
    print_status "Backup created at: $BACKUP_DIR"
    
    # Also backup any existing Docker containers
    if command -v docker &> /dev/null; then
        print_warning "Backing up Docker containers..."
        docker ps -a --format "{{.ID}} {{.Names}}" | grep -i wesza > "$BACKUP_DIR/container-list.txt" 2>/dev/null || true
        print_status "Container list saved"
    fi
else
    print_status "No existing Wesza installation found, skipping backup"
fi

# Step 2: Create swap file (critical for $6 droplet with 1GB RAM)
echo -e "${YELLOW}Step 2: Setting up swap file...${NC}"
if [ ! -f /swapfile ]; then
    fallocate -l $SWAP_SIZE /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' | tee -a /etc/fstab
    print_status "Swap file created ($SWAP_SIZE)"
else
    print_status "Swap file already exists"
fi

# Verify swap is active
swapon --show
print_status "Swap is active"

# Step 3: Install Docker if not present
echo -e "${YELLOW}Step 3: Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    print_warning "Docker not found, installing..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    print_status "Docker installed successfully"
else
    print_status "Docker already installed (version: $(docker --version))"
fi

# Add current user to docker group if not root
if [ "$USER" != "root" ]; then
    usermod -aG docker $USER
    print_warning "Added $USER to docker group. You may need to log out and back in."
fi

# Step 4: Install Docker Compose Plugin
echo -e "${YELLOW}Step 4: Checking Docker Compose...${NC}"
if ! docker compose version &> /dev/null; then
    print_warning "Installing Docker Compose plugin..."
    apt update
    apt install -y docker-compose-plugin
    print_status "Docker Compose installed"
else
    print_status "Docker Compose already installed ($(docker compose version))"
fi

# Step 5: Create Wesza directory structure
echo -e "${YELLOW}Step 5: Setting up Wesza directory...${NC}"
mkdir -p "$WESZA_DIR"
cd "$WESZA_DIR"
print_status "Created directory: $WESZA_DIR"

# Step 6: Upload application files
echo -e "${YELLOW}Step 6: Application files setup${NC}"
print_warning "Upload your Wesza files to $WESZA_DIR using one of these methods:"
echo ""
echo "Method 1 - SCP (from your local machine):"
echo "  scp -r backend/ frontend/ infrastructure/ .env root@YOUR_DROPLET_IP:$WESZA_DIR/"
echo ""
echo "Method 2 - Git Clone:"
echo "  cd $WESZA_DIR && git clone YOUR_REPO_URL . && git checkout main"
echo ""
echo "Method 3 - Create .env file manually:"
echo "  nano $WESZA_DIR/.env"
echo ""

# Create a sample .env file
if [ ! -f "$WESZA_DIR/.env" ]; then
    cat > "$WESZA_DIR/.env.example" << 'EOF'
# === BACKEND ===
ENV=production
PORT=8000

# Database (Supabase)
DATABASE_URL=postgresql://postgres:[password]@db.[project].supabase.co:5432/postgres
SUPABASE_URL=https://[project].supabase.co
SUPABASE_KEY=[your-anon-key]

# Authentication
SECRET_KEY=your-secret-key-change-in-prod-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI (Groq)
GROQ_API_KEY=your-groq-api-key

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
EOF
    print_status "Created .env.example file"
fi

# Step 7: Create Docker Compose file
echo -e "${YELLOW}Step 7: Creating Docker Compose configuration...${NC}"
cat > "$WESZA_DIR/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    container_name: wesza-backend
    restart: unless-stopped
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - ENV=production
    volumes:
      - ./backend/app:/app/app
      - ./backend/logs:/app/logs
    depends_on:
      - redis
    networks:
      - wesza-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build: ./frontend
    container_name: wesza-frontend
    restart: unless-stopped
    ports:
      - "80:80"
    env_file:
      - .env
    depends_on:
      - backend
    networks:
      - wesza-network

  redis:
    image: redis:7-alpine
    container_name: wesza-redis
    restart: unless-stopped
    volumes:
      - redis-data:/data
    networks:
      - wesza-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  wesza-network:
    driver: bridge

volumes:
  redis-data:
EOF
print_status "Docker Compose configuration created"

# Step 8: Create Nginx configuration for reverse proxy
echo -e "${YELLOW}Step 8: Creating Nginx configuration...${NC}"
mkdir -p "$WESZA_DIR/nginx"
cat > "$WESZA_DIR/nginx/nginx.conf" << 'EOF'
server {
    listen 80;
    server_name wesza.online www.wesza.online;

    location / {
        proxy_pass http://frontend:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health check endpoint
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF
print_status "Nginx configuration created"

# Step 9: Build and deploy
echo -e "${YELLOW}Step 9: Building and deploying Wesza...${NC}"
print_warning "This will take a few minutes..."

cd "$WESZA_DIR"

# Check if .env exists
if [ ! -f "$WESZA_DIR/.env" ]; then
    print_error ".env file not found!"
    print_warning "Copy .env.example to .env and fill in your credentials:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Build and start containers
docker compose down --remove-orphans 2>/dev/null || true
docker compose build --no-cache
docker compose up -d

print_status "Containers started!"

# Wait for services to be healthy
echo ""
print_warning "Waiting for services to initialize (this may take 1-2 minutes)..."
sleep 30

# Check container status
echo ""
echo -e "${YELLOW}Container Status:${NC}"
docker compose ps

# Step 10: Show logs
echo ""
echo -e "${YELLOW}Recent logs (last 20 lines):${NC}"
docker compose logs --tail=20

# Step 11: Final instructions
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Wesza Deployment Complete!                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo ""
echo "1. ${YELLOW}Set up Cloudflare Tunnel for HTTPS (recommended):${NC}"
echo "   docker run -d --name cloudflared --restart unless-stopped \\"
echo "     cloudflare/cloudflared:latest tunnel --no-autoupdate run"
echo ""
echo "2. ${YELLOW}Check if services are running:${NC}"
echo "   docker compose ps"
echo ""
echo "3. ${YELLOW}View logs:${NC}"
echo "   docker compose logs -f"
echo ""
echo "4. ${YELLOW}Test the API:${NC}"
echo "   curl http://localhost:8000/api/v1/health"
echo ""
echo "5. ${YELLOW}Access the app:${NC}"
echo "   Frontend: http://YOUR_DROPLET_IP"
echo "   Backend API: http://YOUR_DROPLET_IP:8000/api/v1"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  • Restart:        docker compose restart"
echo "  • Stop:           docker compose down"
echo "  • Update:         docker compose pull && docker compose up -d"
echo "  • Logs:           docker compose logs -f"
echo "  • Shell (backend):docker compose exec backend bash"
echo ""
echo -e "${YELLOW}Backup Location: $BACKUP_DIR${NC}"
echo ""
echo -e "${GREEN}✓ Wesza is now running on your $6 DigitalOcean droplet!${NC}"
echo ""
