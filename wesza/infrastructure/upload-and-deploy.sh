#!/bin/bash
# =============================================================================
# Wesza Platform - Upload & Deploy Script
# Run this from your LOCAL machine to upload and deploy to VPS
# =============================================================================

set -e

# Configuration - UPDATE THESE VALUES
VPS_IP="ubuntu-s-1vcpu-512mb-10gb-lon1-01"
VPS_USER="root"
PROJECT_DIR="/workspace/wesza"

echo "🚀 Wesza Platform - Upload & Deploy"
echo "===================================="
echo ""
echo "Target: ${VPS_USER}@${VPS_IP}"
echo "Source: ${PROJECT_DIR}"
echo ""
read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi

# Step 1: Create remote directory
echo "[1/4] Creating remote directory..."
ssh ${VPS_USER}@${VPS_IP} "mkdir -p /opt/wesza"

# Step 2: Upload backend
echo "[2/4] Uploading backend files..."
rsync -avz --exclude '__pycache__' --exclude '*.pyc' --exclude '.venv' \
    ${PROJECT_DIR}/backend/ ${VPS_USER}@${VPS_IP}:/opt/wesza/backend/

# Step 3: Upload frontend  
echo "[3/4] Uploading frontend files..."
rsync -avz --exclude 'node_modules' --exclude 'dist' --exclude '.vite' \
    ${PROJECT_DIR}/frontend/ ${VPS_USER}@${VPS_IP}:/opt/wesza/frontend/

# Step 4: Upload infrastructure and config
echo "[4/4] Uploading infrastructure files..."
rsync -avz \
    ${PROJECT_DIR}/infrastructure/ ${VPS_USER}@${VPS_IP}:/opt/wesza/infrastructure/
rsync -avz \
    ${PROJECT_DIR}/.env.example \
    ${PROJECT_DIR}/LICENSE \
    ${PROJECT_DIR}/README.md \
    ${VPS_USER}@${VPS_IP}:/opt/wesza/

# Upload docker-compose.yml to root of wesza
if [ -f "${PROJECT_DIR}/infrastructure/docker-compose.yml" ]; then
    cp ${PROJECT_DIR}/infrastructure/docker-compose.yml /tmp/docker-compose-temp.yml
    rsync -avz /tmp/docker-compose-temp.yml ${VPS_USER}@${VPS_IP}:/opt/wesza/docker-compose.yml
    rm /tmp/docker-compose-temp.yml
fi

echo ""
echo "✅ Files uploaded successfully!"
echo ""
echo "📋 Next Steps (run these on your VPS):"
echo "----------------------------------------"
echo "ssh root@${VPS_IP}"
echo "cd /opt/wesza"
echo "chmod +x infrastructure/deploy-to-droplet.sh"
echo "./infrastructure/deploy-to-droplet.sh"
echo ""
echo "Or manually:"
echo "  1. cp .env.example .env"
echo "  2. nano .env  (fill in your credentials)"
echo "  3. docker compose up -d --build"
echo ""
