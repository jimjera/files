#!/bin/bash
# =============================================================================
# Wesza Platform - Quick Deploy (Run directly on VPS)
# This script uploads from /workspace/wesza to /opt/wesza and deploys
# =============================================================================

set -e

echo "🚀 Wesza Platform - Quick Deploy"
echo "================================="
echo ""

SOURCE_DIR="/workspace/wesza"
DEST_DIR="/opt/wesza"

# Check if source exists
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ Error: Source directory $SOURCE_DIR not found!"
    exit 1
fi

# Step 1: Backup existing installation
echo "[1/5] Checking for existing installation..."
if [ -d "$DEST_DIR" ]; then
    BACKUP_DIR="/root/wesza-backup-$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    cp -r "$DEST_DIR" "$BACKUP_DIR/"
    echo "✓ Backed up existing installation to: $BACKUP_DIR"
else
    echo "✓ No existing installation found"
fi

# Step 2: Create destination directory
echo "[2/5] Creating destination directory..."
mkdir -p "$DEST_DIR"

# Step 3: Copy files
echo "[3/5] Copying application files..."
cp -r "$SOURCE_DIR/backend/" "$DEST_DIR/"
cp -r "$SOURCE_DIR/frontend/" "$DEST_DIR/"
cp -r "$SOURCE_DIR/infrastructure/" "$DEST_DIR/"
cp "$SOURCE_DIR/.env.example" "$DEST_DIR/" 2>/dev/null || true
cp "$SOURCE_DIR/LICENSE" "$DEST_DIR/" 2>/dev/null || true
cp "$SOURCE_DIR/README.md" "$DEST_DIR/" 2>/dev/null || true

# Copy docker-compose.yml to root
if [ -f "$SOURCE_DIR/infrastructure/docker-compose.yml" ]; then
    cp "$SOURCE_DIR/infrastructure/docker-compose.yml" "$DEST_DIR/docker-compose.yml"
fi

echo "✓ Files copied to $DEST_DIR"

# Step 4: Check for .env
echo "[4/5] Checking environment configuration..."
cd "$DEST_DIR"
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  WARNING: .env file not found!"
    echo ""
    echo "Please configure your environment:"
    echo "  cd $DEST_DIR"
    echo "  cp .env.example .env"
    echo "  nano .env"
    echo ""
    echo "Required variables:"
    echo "  - DATABASE_URL (Supabase PostgreSQL)"
    echo "  - SUPABASE_URL"
    echo "  - SUPABASE_KEY"
    echo "  - GROQ_API_KEY"
    echo "  - SPACES_KEY, SPACES_SECRET"
    echo "  - SECRET_KEY (generate: openssl rand -hex 32)"
    echo ""
    read -p "Continue after creating .env? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Step 5: Setup swap and Docker if needed
echo "[5/5] Ensuring system dependencies..."

# Setup swap if not exists
if [ ! -f /swapfile ]; then
    echo "Setting up swap space..."
    fallocate -l 4G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "✓ Swap file created (4GB)"
fi

# Install Docker if not exists
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✓ Docker installed"
fi

# Install Docker Compose if not exists
if ! docker compose version &> /dev/null; then
    echo "Installing Docker Compose..."
    apt-get update -qq
    apt-get install -y -qq docker-compose-plugin
    echo "✓ Docker Compose installed"
fi

# Build and start
echo ""
echo "Building and starting containers (this may take 5-10 minutes)..."
docker compose up -d --build

# Wait for health check
echo ""
echo "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✓ Backend is healthy!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "⚠ Backend health check timed out, but containers are running"
        break
    fi
    echo "Waiting... ($i/30)"
    sleep 2
done

# Summary
echo ""
echo "╔════════════════════════════════════════╗"
echo "║   🎉 Wesza Deployed Successfully!     ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "📍 Location: $DEST_DIR"
echo "🔗 Backend: http://localhost:8000"
echo "🔗 Frontend: http://localhost:3000"
echo ""
echo "Useful commands:"
echo "  cd $DEST_DIR"
echo "  docker compose ps          # Status"
echo "  docker compose logs -f     # Logs"
echo "  docker compose restart     # Restart"
echo ""
echo "Access API docs: http://$(curl -s ifconfig.me):8000/docs"
echo ""
